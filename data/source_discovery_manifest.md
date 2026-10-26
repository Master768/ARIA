# Data Source Discovery Manifest: MongoDB `pulse_db`
**Agent:** Arthur (Principal Data Architect & Catalog Locator)  
**Data Source:** MongoDB Atlas (`cluster0.6jegcfk.mongodb.net`)  
**Database:** `pulse_db`  
**Discovered:** 2026-10-26 18:59:20  

---

## 1. Catalog & Entity Overview
Found **3 collection(s)** in `pulse_db`.

| Collection Name | Document Count | Primary Key | Key Attributes | Extracted Path |
|---|---|---|---|---|
| `predictions` | 86 | `_id` (ObjectId) | `_id` (ObjectId), `userId` (ObjectId), `logId` (ObjectId), `productivityScore` (int), `burnoutRisk` (str), `burnoutConfidence` (dict) | `data/raw/pulse_predictions.csv` |
| `users` | 34 | `_id` (ObjectId) | `_id` (ObjectId), `name` (str), `email` (str), `password` (str), `persona` (str), `onboardingComplete` (bool) | `data/raw/pulse_users.csv` |
| `dailylogs` | 85 | `_id` (ObjectId) | `_id` (ObjectId), `userId` (ObjectId), `sleepHours` (float), `studyHours` (int), `screenTimeHours` (int), `exerciseMins` (int) | `data/raw/pulse_dailylogs.csv` |

---

## 2. Detailed Schemas by Collection

### Collection: `predictions`
- **Total Records:** 86
- **Schema Fields:**
  - `_id`: `ObjectId`
  - `userId`: `ObjectId`
  - `logId`: `ObjectId`
  - `productivityScore`: `int`
  - `burnoutRisk`: `str`
  - `burnoutConfidence`: `dict`
  - `primaryConfidence`: `int`
  - `persona`: `str`
  - `clusterId`: `int`
  - `topPositiveFactors`: `list`
  - `topNegativeFactors`: `list`
  - `peer_benchmark`: `dict`
  - `date`: `datetime`
  - `createdAt`: `datetime`
  - `updatedAt`: `datetime`
  - `__v`: `int`
  - `factorContributions`: `list`
  - `personaReason`: `str`
  - `topNegativeFactorsDetailed`: `list`
  - `topPositiveFactorsDetailed`: `list`
  - `isEdited`: `bool`

**Sample Document:**
```json
{
  "_id": "69c8245a16a4c38779564176",
  "userId": "69c803b48bb201e8dcdc138f",
  "logId": "69c8245a16a4c38779564174",
  "productivityScore": 71,
  "burnoutRisk": "Low",
  "burnoutConfidence": {
    "High": 0,
    "Low": 1,
    "Medium": 0
  },
  "primaryConfidence": 1,
  "persona": "Balanced Optimizer",
  "clusterId": 0,
  "topPositiveFactors": [
    "Sleep Quality",
    "Deep Focus",
    "Hydration Level"
  ],
  "topNegativeFactors": [],
  "peer_benchmark": {
    "is_available": false
  },
  "date": "2026-03-28 18:56:26.431000",
  "createdAt": "2026-03-28 18:56:26.671000",
  "updatedAt": "2026-06-15 14:00:21.546000",
  "__v": 0,
  "factorContributions": [
    {
      "avg": 227,
      "feature": "focus_duration_mins",
      "impact": -33.51,
      "value": 0
    },
    {
      "avg": 5.944135,
      "feature": "sleep_hours",
      "impact": 5.91,
      "value": 7.5
    },
    {
      "avg": 1,
      "feature": "distraction_level_encoded",
      "impact": 5.2,
      "value": 0
    },
    {
      "avg": 3.4507,
      "feature": "deep_focus_blocks",
      "impact": 5.15,
      "value": 2
    },
    {
      "avg": 2.307828,
      "feature": "water_litres",
      "impact": 4.67,
      "value": 2
    },
    {
      "avg": 2.964698,
      "feature": "stress_level",
      "impact": 3.74,
      "value": 2
    },
    {
      "avg": 3.67,
      "feature": "focus_quality_score",
      "impact": 3.57,
      "value": 5
    },
    {
      "avg": 3.295959,
      "feature": "mood_score",
      "impact": 3,
      "value": 4
    },
    {
      "avg": 5.289651,
      "feature": "screen_time_hours",
      "impact": 2.14,
      "value": 4
    },
    {
      "avg": 2.75049,
      "feature": "caffeine_intake",
      "impact": 0.97,
      "value": 2
    },
    {
      "avg": 6.214414,
      "feature": "study_hours",
      "impact": 0.42,
      "value": 6
    },
    {
      "avg": 27.55959,
      "feature": "exercise_mins",
      "impact": 0.2,
      "value": 30
    },
    {
      "avg": 110.88499,
      "feature": "social_media_mins",
      "impact": 0.02,
      "value": 60
    }
  ],
  "personaReason": "Behavior patterns align with historical consistency.",
  "topNegativeFactorsDetailed": [],
  "topPositiveFactorsDetailed": [
    {
      "impact": 5.91,
      "insight": "Optimal sleep duration is restoring your cognitive faculties. (+5.91 pts)",
      "label": "Sleep Quality"
    },
    {
      "impact": 5.15,
      "insight": "Consistent deep work blocks are maximizing your efficiency. (+5.15 pts)",
      "label": "Deep Focus"
    },
    {
      "impact": 4.67,
      "insight": "Excellent hydration is maintaining cellular focus. (+4.67 pts)",
      "label": "Hydration Level"
    }
  ]
}
```

---
### Collection: `users`
- **Total Records:** 34
- **Schema Fields:**
  - `_id`: `ObjectId`
  - `name`: `str`
  - `email`: `str`
  - `password`: `str`
  - `persona`: `str`
  - `onboardingComplete`: `bool`
  - `createdAt`: `datetime`
  - `updatedAt`: `datetime`
  - `__v`: `int`
  - `goalPersona`: `str`
  - `lastBalancedDate`: `datetime`
  - `streakCount`: `int`

**Sample Document:**
```json
{
  "_id": "69c7f08c862f5db20475cd56",
  "name": "Trend Simulator",
  "email": "simulator@test.com",
  "password": "[REDACTED_BCRYPT_HASH]",
  "persona": "balanced",
  "onboardingComplete": true,
  "createdAt": "2026-03-28 15:15:25.006000",
  "updatedAt": "2026-03-28 15:15:25.193000",
  "__v": 0
}
```

---
### Collection: `dailylogs`
- **Total Records:** 85
- **Schema Fields:**
  - `_id`: `ObjectId`
  - `userId`: `ObjectId`
  - `sleepHours`: `float`
  - `studyHours`: `int`
  - `screenTimeHours`: `int`
  - `exerciseMins`: `int`
  - `moodScore`: `int`
  - `stressLevel`: `int`
  - `caffeineIntake`: `int`
  - `waterLitres`: `int`
  - `deepFocusBlocks`: `int`
  - `socialMediaMins`: `int`
  - `focus_duration_mins`: `int`
  - `focus_quality_score`: `int`
  - `distraction_level`: `str`
  - `distraction_level_encoded`: `int`
  - `has_focus_session`: `bool`
  - `is_completed`: `bool`
  - `date`: `datetime`
  - `dayOfWeek`: `str`
  - `isWeekend`: `bool`
  - `createdAt`: `datetime`
  - `updatedAt`: `datetime`
  - `__v`: `int`
  - `dayKey`: `str`

**Sample Document:**
```json
{
  "_id": "69c8245a16a4c38779564174",
  "userId": "69c803b48bb201e8dcdc138f",
  "sleepHours": 7.5,
  "studyHours": 6,
  "screenTimeHours": 4,
  "exerciseMins": 30,
  "moodScore": 4,
  "stressLevel": 2,
  "caffeineIntake": 2,
  "waterLitres": 2,
  "deepFocusBlocks": 2,
  "socialMediaMins": 60,
  "focus_duration_mins": 0,
  "focus_quality_score": 5,
  "distraction_level": "None",
  "distraction_level_encoded": 0,
  "has_focus_session": true,
  "is_completed": true,
  "date": "2026-03-28 18:56:26.431000",
  "dayOfWeek": "Sunday",
  "isWeekend": true,
  "createdAt": "2026-03-28 18:56:26.588000",
  "updatedAt": "2026-03-28 18:57:08.476000",
  "__v": 0
}
```

---

## 3. Downstream Handoff to Maya (Data Understanding)
- Extracted datasets are safely landed in `data/raw/pulse_*.csv` and `data/raw/pulse_*.parquet`.
- Maya can now profile distributions, missingness, and correlation across these collections!
