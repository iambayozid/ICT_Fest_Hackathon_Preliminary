# Bug Report: CoWork API

This document lists all the bugs found and fixed in the CoWork API project. Each bug includes a simple explanation of what went wrong and which rule from the problem statement it violated.

## 1. Authentication & Users

- **Token Expiration Time was Too Long**
  - **What was wrong:** The code multiplied the token time incorrectly, making access tokens last for 15 hours instead of 15 minutes.
  - **Rule Violated:** Rule 8 (Access tokens expire in exactly 900 seconds).

- **Logout Blocked the Wrong Target**
  - **What was wrong:** When a user logged out, the system blocked their User ID (`sub`) instead of the specific Token ID (`jti`). This accidentally logged them out of all their devices at once instead of just the current session.
  - **Rule Violated:** Rule 8 (Logout immediately invalidates the presented access token).

- **Reusable Refresh Tokens**
  - **What was wrong:** The system did not track when a refresh token was used, meaning a user could keep using the same one forever to get new access tokens.
  - **Rule Violated:** Rule 8 (Refresh tokens are single-use).

- **Duplicate Username Race Condition**
  - **What was wrong:** If two people tried to register the exact same username at the exact same millisecond, the system would crash or accept both instead of stopping the second person.
  - **Rule Violated:** Rule 15 (A duplicate username within the org -> 409 USERNAME_TAKEN).

## 2. Booking Rules & Time

- **Blocked Back-to-Back Bookings**
  - **What was wrong:** The conflict checker used a "less than or equal to" (`<=`) math symbol instead of strictly "less than" (`<`). This meant if one meeting ended at 2:00 PM, another couldn't start exactly at 2:00 PM.
  - **Rule Violated:** Rule 3 (Back-to-back bookings are allowed).

- **Booking in the Past (Grace Period)**
  - **What was wrong:** The code allowed a secret 5-minute grace period, letting users book rooms for times that had already passed.
  - **Rule Violated:** Rule 2 (start_time must be strictly in the future at request time — no grace window).

- **Missing End Time & Duration Checks**
  - **What was wrong:** The system never checked if a booking's end time happened _before_ the start time, and it didn't enforce the minimum 1-hour duration.
  - **Rule Violated:** Rule 2 (Minimum 1 hour, end_time must be strictly after start_time).

- **Overwriting Start Time on View**
  - **What was wrong:** When viewing a single booking (`GET /bookings/{id}`), the response accidentally replaced the booking's `start_time` with the time the booking was created (`created_at`).
  - **Rule Violated:** Section 5 (Request / Response Schemas for Bookings).

- **Timezone Stripping**
  - **What was wrong:** When users sent dates with timezones, the system chopped the timezone off without converting the time to UTC first, saving the wrong time to the database.
  - **Rule Violated:** Rule 1 (Input datetimes carrying a UTC offset must be converted to UTC before storage).

## 3. Refunds & Cancellations

- **Exactly 48-Hour Notice Bug**
  - **What was wrong:** If a user canceled at _exactly_ 48 hours notice, the system gave them a 100% refund. The rules say it must be strictly _more_ than 48 hours to get 100%.
  - **Rule Violated:** Rule 6 (Notice > 48 hours = 100% refund).

- **Under 24-Hour Notice Bug**
  - **What was wrong:** If a user canceled with less than 24 hours of notice, they were given a 50% refund instead of the required 0% refund.
  - **Rule Violated:** Rule 6 (Notice < 24 hours = 0% refund).

- **Wrong Math for Half-Cents**
  - **What was wrong:** The system used basic number chopping (`int()`) to round refunds. If a refund was 12.5 cents, it chopped it down to 12 instead of correctly rounding up to 13.
  - **Rule Violated:** Rule 6 (Refund amount rounds to the nearest cent, half-cents rounding up).

## 4. Visibility & Permissions (Multi-Tenancy)

- **Members Seeing Other People's Bookings**
  - **What was wrong:** Regular members could type in another person's booking ID and view their private booking details.
  - **Rule Violated:** Rule 10 (Members may read and cancel only their own bookings).

- **Admins Blind to Organization Bookings**
  - **What was wrong:** When an Admin asked for a list of bookings (`GET /bookings`), the code wrongly filtered the list to only show the Admin's _personal_ bookings, hiding the rest of the company's schedule from them.
  - **Rule Violated:** Rule 10 (Admins may read and cancel any booking in their org).

- **Export Tool Blindness**
  - **What was wrong:** Similar to the bug above, Admins couldn't export the whole company's data unless they checked a specific `include_all` box. It wrongly filtered to their personal bookings by default.
  - **Rule Violated:** Rule 10 (Admins may read any booking in their org).

- **Cross-Organization Room Bypass**
  - **What was wrong:** If an Admin tried to export data for a Room ID that belonged to a _different_ company, the system gave them a blank successful file instead of throwing an error.
  - **Rule Violated:** Rule 9 (Cross-org resource IDs behave as non-existent -> 404).

## 5. Live Data, Performance, & Systems

- **Broken Pagination (Skipping Pages)**
  - **What was wrong:** The math for loading pages was wrong (`page * limit`), which caused the system to completely skip the first page of results. It also sorted them backward.
  - **Rule Violated:** Rule 11 (Sequential pages never skip or repeat items, sorted ascending).

- **Rate Limit Spammer Cheat**
  - **What was wrong:** If a user spammed the booking button too fast, the system blocked them but didn't record the blocked attempts. This allowed attackers to wait out the penalty faster than intended.
  - **Rule Violated:** Rule 5 (all requests count).

- **Missing Simultaneous Safety (Concurrency)**
  - **What was wrong:** If multiple people used the app at the exact same millisecond, the system would crash or double-book rooms because there were no thread locks for generating reference codes, live stats, or sending notifications.
  - **Rule Violated:** Rule 16 (No combination of concurrent valid requests may hang the service) and Rule 7 (Reference codes unique under concurrent creation).

- **Stale Usage Reports**
  - **What was wrong:** When a new booking was made, the admin "Usage Report" cache was not cleared. Admins would see outdated numbers until someone canceled a booking.
  - **Rule Violated:** Rule 12 (Must reflect the current state immediately).

- **Amnesia on Server Restart (Stats Reset)**
  - **What was wrong:** If the server was restarted, the live room statistics tracking memory reset to zero. It did not check the database to remember past bookings.
  - **Rule Violated:** Rule 14 (Stats must always be consistent with the bookings themselves).

## 6. Formatting

- **Wrong CSV Header Text**
  - **What was wrong:** The export file outputted the column name as `start_time` (with an underscore) instead of `start time` (with a space).
  - **Rule Violated:** Section 5 (Export CSV header exact match).
