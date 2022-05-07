# backendhackchallenge
This repository contains the backend code for our app PlanMate.

We have 3 tables—an Event, User, and Task table.

The User table contains all the users in our app, including username and (hashed) password for each.

The Event table contains all the events ever made in our app. Each event has a lot of properties, including name, description, start time, end time, color, and location.
- Start time and end time are integers that represent Unix epoch time (i.e. the number of seconds since January 1, 1970 that have passed).
- Color is a string that stores a hex code (e.g. "#FFFFFF").

The Task table contains all the tasks ever made in our app. Each task has a lot of properties, including name, due date, completed, and priority.
- Due date is an integer representing Unix epoch time (i.e. the number of seconds since January 1, 1970 that have passed)
- Priority is an integer that ranges from 0-2 (0 = low, 1 = medium, 2 = high)

The User table is linked to the Event table in a one-to-many relationship, with a foreign key in each event referencing the user id of the user the event belongs to.

The User table is linked to the Task table in a one-to-many relationship, with a foreign key in each task referencing the user id of the user the task belongs to.

All of our rotes are described in our API specification document.
