# Garmin Developer Program Registration Description

Use the following description when registering for the Garmin Developer Program.

---

## How do you plan to use the Garmin Connect Developer Program?

**Recommended Description:**

```
StepSquad is a web-based platform that enables users to participate in team-based step competitions and challenges. 

We plan to use the Garmin Connect Developer Program to:

1. **Sync Step Data**: Allow users to connect their Garmin devices and automatically sync their daily step counts to participate in competitions.

2. **Competition Participation**: Enable users to join team-based step challenges where their Garmin step data is automatically submitted to team competitions.

3. **Real-time Leaderboards**: Display real-time leaderboards showing team standings based on aggregated step data from all connected Garmin devices.

4. **Health Motivation**: Help users stay motivated and active by participating in friendly team competitions with their Garmin fitness data.

Our application will:
- Use OAuth 1.0a to authenticate users and request access to their Garmin Connect wellness data
- Fetch daily step summaries from the Garmin Wellness API
- Display aggregated team step counts in leaderboards
- Allow users to participate in time-bound step competitions

The data accessed will be limited to:
- Daily step counts
- Activity summaries (step data only)
- No personal identifying information beyond what's necessary for competition participation

All data access follows user consent via OAuth, and users can revoke access at any time. We comply with all Garmin Developer Program terms and conditions, and we maintain user privacy and data security standards.
```

---

## Alternative Shorter Version

If the form has character limits, use this shorter version:

```
StepSquad is a web-based platform for team-based step competitions. We will use the Garmin Connect Developer Program to:

1. Allow users to connect their Garmin devices via OAuth
2. Automatically sync daily step counts to participate in team competitions
3. Display real-time leaderboards showing team standings based on aggregated step data

We will only access:
- Daily step summaries from the Wellness API
- Activity data needed for competition participation

All access is user-authorized via OAuth, and users can revoke access at any time. We comply with Garmin Developer Program terms and maintain user privacy standards.
```

---

## Alternative One-Paragraph Version

If the form requires a single paragraph:

```
StepSquad is a web-based platform that enables users to participate in team-based step competitions by syncing their Garmin device data. We plan to use the Garmin Connect Developer Program to allow users to connect their Garmin devices via OAuth authentication and automatically sync their daily step counts to participate in team competitions. Our application will fetch daily step summaries from the Garmin Wellness API and display aggregated team step counts in real-time leaderboards. All data access follows user consent via OAuth, and users can revoke access at any time. We comply with all Garmin Developer Program terms and conditions and maintain strict user privacy and data security standards.
```

---

## Key Points to Include

When filling out the registration form, make sure to emphasize:

1. ✅ **Purpose**: Team-based step competitions
2. ✅ **Data Usage**: Only step counts, no personal identifying information
3. ✅ **User Consent**: OAuth-based user authorization
4. ✅ **Privacy**: Users can revoke access, we comply with terms
5. ✅ **API Usage**: Wellness API for daily step summaries
6. ✅ **Security**: We maintain data security standards

---

## Application Details (Other Fields)

When filling out other fields in the registration form:

**Application Name**: `StepSquad`

**Company/Organization**: `Tekolin` (or your organization name)

**Application Description**: 
```
StepSquad is a web-based platform for team-based step competitions that allows users to connect their Garmin devices and automatically sync step data to participate in challenges and view leaderboards.
```

**Application Website**: `https://www.stepsquad.club`

**Terms of Service**: `https://stepsquad.club/terms`

**Privacy Policy**: `https://stepsquad.club/privacy`

**Application Type**: `Web Application` or `Server Application`

**API Access Needed**: 
- Wellness API (for step data)
- Activity API (for daily summaries)

---

## Tips for Registration

1. **Be Specific**: Clearly explain what you'll do with the API
2. **Emphasize Privacy**: Show you respect user data and privacy
3. **Mention OAuth**: Show you understand authentication requirements
4. **Limited Scope**: Only request access to data you actually need (step counts)
5. **Compliance**: Mention you'll comply with terms and conditions
6. **User Control**: Emphasize users can revoke access anytime

---

## After Registration

After submitting the registration:

1. ✅ **Wait for Approval**: Garmin typically reviews applications within 1-3 business days
2. ✅ **Check Email**: You'll receive an email when your application is approved
3. ✅ **Create OAuth Client**: After approval, you can create OAuth clients
4. ✅ **Get Credentials**: You'll receive Consumer Key and Consumer Secret
5. ✅ **Configure Environment**: Set up environment variables (see `GARMIN_APP_SETUP.md`)

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Registration

