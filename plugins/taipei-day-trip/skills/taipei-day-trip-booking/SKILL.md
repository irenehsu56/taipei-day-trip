---
name: taipei-day-trip-booking
description: Search for Taipei attractions by keyword and add a selected attraction, date, and time to the Taipei Day Trip booking cart through its MCP server. Use when a user wants to search Taipei attractions and create a Taipei Day Trip booking.
---

# Taipei Day Trip Booking

Follow this workflow in order. Use the `taipei-day-trip` MCP server for searching and booking.

## Workflow

1. Ask the user to enter a search keyword for Taipei attractions.
2. Pass the keyword to the search tool provided by the Taipei Day Trip MCP.
3. Show the search results. Include at least each attraction's `id` and `name`.
4. Ask the user, in natural language, for all three booking values:
   - attraction id
   - date
   - time
5. Convert the user's response into this preferred format:

   ```yaml
   attraction_id: 123
   date: 2026-09-18
   time: morning
   price: 2000
   ```

   Apply these rules:
   - Convert `attraction_id` to an integer.
   - Convert `date` to `YYYY-MM-DD`.
   - Convert `time` to exactly `morning` or `afternoon`.
   - Treat morning as 9:00 AM to 4:00 PM and set `price` to `2000`.
   - Treat afternoon as 2:00 PM to 9:00 PM and set `price` to `2500`.
   - Derive `price` from `time`; do not ask the user for a price.
   - If any value is missing or cannot be converted unambiguously, ask only for the missing or ambiguous value before continuing.
6. Call the Taipei Day Trip MCP booking or add-to-cart tool with all four required parameters: `attraction_id`, `date`, `time`, and `price`.
7. After the tool reports a successful booking, show the Booking Page link returned by the tool so the user can complete the order.

Do not add comparison, party-size, traveler-information, cancellation, refund, or payment-confirmation workflows. Do not claim that a booking succeeded unless the MCP tool reports success.
