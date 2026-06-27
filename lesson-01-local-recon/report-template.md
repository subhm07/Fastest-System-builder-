# Lesson 01 Report: Local Recon Practical

## Scope
- Authorized target: 127.0.0.1 only
- Environment: Local WSL lab
- Date/time:

## Objective
Understand how to identify local network configuration, listening services, open TCP ports, and HTTP service metadata.

## Commands Used
```bash
ip -br addr
ip route
ss -tulnp
python3 local_recon.py
curl -I http://127.0.0.1:8080/
```

## Key Observations
| Observation | Evidence | Security Meaning |
|---|---|---|
| Local web service exposed | 127.0.0.1:8080 open | Service is reachable locally |
| HTTP header reveals server | SimpleHTTP Python version | Banner disclosure can help fingerprint technology |
| Other common ports closed | 22/80/443 closed | Reduced local attack surface |

## Risk Analysis
- Exposed services increase attack surface.
- Service banners may reveal technology stack and version.
- Binding to 127.0.0.1 limits exposure to local machine only.
- Binding to 0.0.0.0 would expose the service on all interfaces and increase risk.

## Detection Opportunities
Linux:
```bash
ss -tulnp
journalctl
```

Windows/Sentinel angle:
```kql
DeviceNetworkEvents
| where RemotePort in (22,80,443,8080)
| summarize ConnectionCount=count() by DeviceName, InitiatingProcessFileName, RemoteIP, RemotePort, bin(Timestamp, 5m)
| order by ConnectionCount desc
```

Sysmon angle:
- Event ID 3: Network connection

## Remediation / Hardening
- Bind local-only services to 127.0.0.1.
- Disable services not required.
- Avoid revealing unnecessary version information.
- Monitor unexpected listening ports.
- Restrict access using firewall rules.

## What I Learned
-
-
-
