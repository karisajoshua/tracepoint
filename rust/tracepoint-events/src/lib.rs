//! Typed security event validation and normalization.
//!
//! This is a standalone Rust foundation, not yet connected to the FastAPI ingestion
//! path. Keep wire compatibility explicit and test changes against Python contracts.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::net::IpAddr;
use std::str::FromStr;
use uuid::Uuid;

pub const MAX_SOURCE_LENGTH: usize = 80;
pub const MAX_EVENT_TYPE_LENGTH: usize = 100;
pub const MAX_ACTOR_LENGTH: usize = 128;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SecurityEvent {
    pub event_id: Uuid,
    pub source: String,
    pub event_type: String,
    pub timestamp: DateTime<Utc>,
    pub actor_id: Option<String>,
    pub source_ip: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum EventError {
    InvalidJson(String),
    InvalidField(&'static str),
    InvalidIp,
}

impl std::fmt::Display for EventError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InvalidJson(reason) => write!(f, "invalid event JSON: {reason}"),
            Self::InvalidField(field) => write!(f, "invalid field: {field}"),
            Self::InvalidIp => write!(f, "source_ip must be a valid IPv4 or IPv6 address"),
        }
    }
}

impl std::error::Error for EventError {}

fn clean_required(value: &mut String, max: usize, field: &'static str) -> Result<(), EventError> {
    *value = value.trim().to_owned();
    if value.is_empty()
        || value.len() > max
        || value.chars().any(|ch| ch.is_control())
    {
        return Err(EventError::InvalidField(field));
    }
    Ok(())
}

/// Parse a single JSON event, enforce field constraints, and canonicalize IP addresses.
///
/// This function is deterministic and does not access the network or database.
pub fn parse_and_normalize(json: &str) -> Result<SecurityEvent, EventError> {
    let mut event: SecurityEvent =
        serde_json::from_str(json).map_err(|err| EventError::InvalidJson(err.to_string()))?;

    clean_required(&mut event.source, MAX_SOURCE_LENGTH, "source")?;
    clean_required(&mut event.event_type, MAX_EVENT_TYPE_LENGTH, "event_type")?;

    if let Some(actor) = &event.actor_id {
        if actor.len() > MAX_ACTOR_LENGTH {
            return Err(EventError::InvalidField("actor_id"));
        }
    }

    if let Some(ip) = &event.source_ip {
        let parsed = IpAddr::from_str(ip).map_err(|_| EventError::InvalidIp)?;
        event.source_ip = Some(parsed.to_string());
    }
    Ok(event)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn payload(ip: &str) -> String {
        format!(
            r#"{{"event_id":"123e4567-e89b-42d3-a456-426614174000","source":" demo ","event_type":"auth.login_failed","timestamp":"2026-10-14T12:00:00Z","actor_id":null,"source_ip":"{ip}"}}"#
        )
    }

    #[test]
    fn accepts_valid_ipv4() {
        let event = parse_and_normalize(&payload("192.0.2.10")).unwrap();
        assert_eq!(event.source, "demo");
        assert_eq!(event.source_ip.as_deref(), Some("192.0.2.10"));
    }

    #[test]
    fn canonicalizes_ipv6() {
        let event = parse_and_normalize(&payload("2001:0DB8:0000:0000:0000:0000:0000:0001")).unwrap();
        assert_eq!(event.source_ip.as_deref(), Some("2001:db8::1"));
    }

    #[test]
    fn rejects_invalid_ip() {
        assert_eq!(parse_and_normalize(&payload("999.0.0.1")).unwrap_err(), EventError::InvalidIp);
    }

    #[test]
    fn rejects_control_characters() {
        let input = payload("192.0.2.10").replace("auth.login_failed", "auth\\nlogin_failed");
        assert_eq!(parse_and_normalize(&input).unwrap_err(), EventError::InvalidField("event_type"));
    }

    #[test]
    fn rejects_unknown_fields() {
        let input = payload("192.0.2.10").replace(r#""actor_id":null"#, r#""actor_id":null,"admin":true"#);
        assert!(matches!(parse_and_normalize(&input), Err(EventError::InvalidJson(_))));
    }

    #[test]
    fn rejects_whitespace_only_source() {
        let input = payload("192.0.2.10").replace(" demo ", "   ");
        assert_eq!(parse_and_normalize(&input).unwrap_err(), EventError::InvalidField("source"));
    }

    #[test]
    fn rejects_naive_timestamps() {
        let input = payload("192.0.2.10").replace("2026-10-14T12:00:00Z", "2026-10-14T12:00:00");
        assert!(matches!(parse_and_normalize(&input), Err(EventError::InvalidJson(_))));
    }

    #[test]
    fn serialization_round_trip() {
        let event = parse_and_normalize(&payload("192.0.2.10")).unwrap();
        let serialized = serde_json::to_string(&event).unwrap();
        assert_eq!(parse_and_normalize(&serialized).unwrap(), event);
    }
}
