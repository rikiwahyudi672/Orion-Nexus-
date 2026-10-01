# ARCHITECTURE

## Overview
Orion v2.7 - asisten pribadi AI.

## Modul
### Core
orion.py, orion_hub.py (31 fungsi), otak_orion.py (83KB), orion_neural.py

### Emotion
emotion_orion.py, emotion_decay.py, mood_orion.py

### Memory
experience_hub.py, memory_orion.py, memory_manager.py

### Automation (14 pipeline)
cron_orion.py, cron_llm.py, orion_background.py, auto_distill.py, inisiatif_orion.py, maintenance_orion.py, notif_orion.py, orion_update.py

### Skill
skill_loader.py, skill_installer.py, skill_curator.py

## Database (36 tabel)
- chat, log_aksi, skill_log
- experience, pengalaman, fakta
- mood_state, mood_events, emotion_state
- relationship, loyalty
- agents, agent_tasks
- dll

## Pipeline (14)
cron, background, distill, inisiatif, maintenance, notif, update, face, wake, voice, stream, web, dashboard

## Cron (9 task)
08:00, 09:30, 12:00, 15:00, 17:30, 20:00, 22:00, 23:30, 03:00

## Status
- 15 modul hidup, 0 error
- 15 skill aktif (193 file)
- 36 tabel database
