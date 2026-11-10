# Startinstruktion till Claude Code

Projektet heter **Magic Rain**. Här finns en komplett WDD (Working Design Document), agentinstruktioner och en byggplan. Följ specifikationen i repositoryt.

**Börja med att läsa `AGENTS.md`, `CLAUDE.md`, `WDD/README.md`, `docs/claude/FIRST_PROMPT.md` och roadmapen.** Implementera endast **MR-00** i första omgången. Bygg en demo av magiskt regn med simulerad Kinect för den befintliga datorn med Windows 10 Pro 22H2. Redovisa en kort, skrivskyddad hårdvaruförkontroll enligt `docs/setup/tv-first-preflight.md`.

Barnupplevelsen är helig: ingen HUD, inga instruktioner, inga ikoner, inga poäng eller knappar under lek. Barnet ska bara gå framför kameran; regnet ska reagera på kroppens silhuett, rörelse, sträckning och poser så naturligt att förklaring inte behövs. Riktig Kinect v1-hårdvara är en senare verifieringsgrind. Efter MR-00 ska faktisk Kinect-drift prioriteras så snart sensorn och rätt adapter är tillgängliga. Projektor, klättervägg, bollkastning och spelkonsolkoppling ingår **inte** i denna version och ska inte förberedas med extra kod. Säg uttryckligen när något bara fungerar i demosimuleringen.

Följ principen en issue per PR, WDD-först när designen ändras, automatiska tester, en fristående granskningsrunda och ingen bloat. Rapportera vad som faktiskt fungerar, vilka tester som körts och nästa fas — utan att påstå att hårdvara verifierats utan ett riktigt test.

Den mer detaljerade prompten finns i `docs/claude/FIRST_PROMPT.md` och är normerande om den avviker från denna svenska introduktion.
