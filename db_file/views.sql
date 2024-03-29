CREATE VIEW "v_users" AS SELECT "user_id", "name" FROM "users";

CREATE VIEW "v_users_login" AS SELECT "user_id", "name", "login" FROM "users";

CREATE VIEW "v_user_cols" AS SELECT "user_id", "cols_order" FROM "users";

CREATE VIEW "v_personal_tasks" AS
SELECT "task_id", "description", "start_date", "end_date", "done", "user_id", "col_id"
FROM "personal_tasks";

CREATE VIEW "v_command" AS 
SELECT "commands"."command_id", "name", "owner_id", "user_id"
FROM "commands"
INNER JOIN "commands_user"
ON "commands_user"."command_id" = "commands"."command_id";

CREATE VIEW "v_command_cols" AS SELECT "command_id", "cols_order" FROM "commands";

CREATE VIEW "v_command_tasks" AS
SELECT "tasks"."task_id", "description", "start_date", "end_date", "done", "performer_id", "col_id",
        "users"."name", "groups"."color", "groups"."name" as "group_name"
FROM "tasks"
INNER JOIN "commands_task"
ON "tasks"."task_id" = "commands_task"."task_id"
INNER JOIN "users"
ON "tasks"."performer_id" = "users"."user_id"
INNER JOIN "groups"
ON "commands_task"."group_id" = "groups"."group_id";

CREATE VIEW "v_command_tasks_group" AS
SELECT "tasks"."task_id", "description", "start_date", "end_date", "done",
        "performer_id", "users"."name", "commands_task"."group_id"
FROM "tasks"
INNER JOIN "commands_task"
ON "tasks"."task_id" = "commands_task"."task_id"
INNER JOIN "users"
ON "tasks"."performer_id" = "users"."user_id";

CREATE VIEW "v_group" AS
SELECT "groups"."group_id", "groups"."name", "color", "groups"."command_id",
        "groups"."owner_id", "blocked", "user_id", "commands"."owner_id" as "command_owner_id"
FROM "groups"
INNER JOIN "groups_user"
ON "groups"."group_id" = "groups_user"."group_id"
INNER JOIN "commands"
ON "groups"."command_id" = "commands"."command_id";

CREATE VIEW "v_group_owner" AS
SELECT "groups"."name", "color", "groups"."command_id", "groups"."owner_id"
FROM "groups"
INNER JOIN "commands"
ON "groups"."command_id" = "commands"."command_id";

CREATE VIEW "v_group_cols" AS SELECT "group_id", "cols_order" FROM "groups";

CREATE VIEW "v_group_tasks" AS
SELECT "tasks"."task_id", "description", "start_date", "end_date", "done", "performer_id",
        "col_id", "users"."name"
FROM "tasks"
INNER JOIN "users"
ON "tasks"."performer_id" = "users"."user_id";

CREATE VIEW "v_personal_events" AS
SELECT *
FROM "personal_events"
ORDER BY "personal_events"."date";

CREATE VIEW "v_command_events" AS
SELECT "events".*, "commands_event"."command_id", "users_event"."user_id", "users_event"."done"
FROM "events"
INNER JOIN "commands_event"
ON "commands_event"."event_id" = "events"."event_id"
INNER JOIN "users_event"
ON "users_event"."event_id" = "events"."event_id"
ORDER BY "events"."date";

CREATE VIEW "v_group_events" AS
SELECT "events".*, "groups_event"."group_id", "users_event"."user_id", "users_event"."done"
FROM "events"
INNER JOIN "groups_event"
ON "groups_event"."event_id" = "events"."event_id"
INNER JOIN "users_event"
ON "users_event"."event_id" = "events"."event_id"
ORDER BY "events"."date";
