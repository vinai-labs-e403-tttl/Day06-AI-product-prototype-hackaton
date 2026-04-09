<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/cfd5bc51-7f3e-43de-9bea-cc99e958b75c

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key
3. Run the app:
   `npm run dev`

```sh
curl -X POST -H 'content-type: application/json' -d '{
  "origin": {
    "address": "Cầu Giấy, Hà Nội"
  },
  "destination": {
    "address": "Vinhome Ocean Park 1"
  },
  "travelMode": "TRANSIT",
  "computeAlternativeRoutes": true,
  "transitPreferences": {
     routingPreference: "LESS_WALKING",
     allowedTravelModes: ["TRAIN"]
  },
}' \
-H 'Content-Type: application/json' \
-H 'X-Goog-Api-Key: AIzaSyDG14sihEbdlSVR2ruIJV599JXS5vP9r4g' \
-H 'X-Goog-FieldMask: routes.legs.steps.transitDetails.transitLine.nameShort,routes.legs.steps.transitDetails.stopDetails.departureStop.name,routes.legs.steps.transitDetails.stopDetails.arrivalStop.name,routes.legs.steps.transitDetails.localizedValues.departureTime.time.text,routes.legs.steps.transitDetails.localizedValues.arrivalTime.time.text,routes.legs.steps.transitDetails.stopCount' \
'https://routes.googleapis.com/directions/v2:computeRoutes'
```