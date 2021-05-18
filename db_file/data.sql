BEGIN TRANSACTION;
INSERT INTO "users" VALUES (1,'mrs','b21dabb4c22d87c7e22f179206f3fa06efe0e6379df60ee5cfca87bea6efd236','Сашко','1,2');
INSERT INTO "users" VALUES (2,'s0fko','a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3','Софійка','15,16');
INSERT INTO "users" VALUES (3,'test','9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08','test','17,18');
INSERT INTO "commands" VALUES (1,'Command 1',1,'3,4');
INSERT INTO "commands" VALUES (2,'Command 2',2,'5,6');
INSERT INTO "commands" VALUES (3,'Command 3',1,'7,8');
INSERT INTO "commands_user" VALUES (1,1);
INSERT INTO "commands_user" VALUES (2,1);
INSERT INTO "commands_user" VALUES (3,1);
INSERT INTO "commands_user" VALUES (1,2);
INSERT INTO "commands_user" VALUES (2,2);
INSERT INTO "commands_user" VALUES (3,2);
INSERT INTO "commands_user" VALUES (1,3);
INSERT INTO "commands_user" VALUES (2,3);
INSERT INTO "groups" VALUES (1,'1 group 1 command','#35655a',1,1,0,'9,10');
INSERT INTO "groups" VALUES (2,'2 group 1 command','#adbb95',1,2,0,NULL);
INSERT INTO "groups" VALUES (3,'3 group 2 command','#f5b175',2,2,0,'11,12');
INSERT INTO "groups" VALUES (4,'4 group 2 command','#d76459',2,3,0,NULL);
INSERT INTO "groups" VALUES (5,'5 group 3 command','#c52e39',3,2,0,'13,14');
INSERT INTO "groups" VALUES (6,'6 group 3 command','#72d0bd',3,2,0,NULL);
INSERT INTO "groups_user" VALUES (1,1);
INSERT INTO "groups_user" VALUES (2,1);
INSERT INTO "groups_user" VALUES (3,1);
INSERT INTO "groups_user" VALUES (1,2);
INSERT INTO "groups_user" VALUES (2,2);
INSERT INTO "groups_user" VALUES (1,3);
INSERT INTO "groups_user" VALUES (2,3);
INSERT INTO "groups_user" VALUES (3,3);
INSERT INTO "groups_user" VALUES (2,4);
INSERT INTO "groups_user" VALUES (3,4);
INSERT INTO "groups_user" VALUES (1,5);
INSERT INTO "groups_user" VALUES (2,5);
INSERT INTO "groups_user" VALUES (1,6);
INSERT INTO "groups_user" VALUES (2,6);
INSERT INTO "cols" VALUES (1,'Planned mrs');
INSERT INTO "cols" VALUES (2,'In work mrs');
INSERT INTO "cols" VALUES (3,'3 column 1 command');
INSERT INTO "cols" VALUES (4,'4 column 1 command');
INSERT INTO "cols" VALUES (5,'5 column 2 command');
INSERT INTO "cols" VALUES (6,'6 column 2 command');
INSERT INTO "cols" VALUES (7,'7 column 3 command');
INSERT INTO "cols" VALUES (8,'8 column 3 command');
INSERT INTO "cols" VALUES (9,'9 column 1 group');
INSERT INTO "cols" VALUES (10,'10 column 1 group');
INSERT INTO "cols" VALUES (11,'11 column 3 group');
INSERT INTO "cols" VALUES (12,'12 column 3 group');
INSERT INTO "cols" VALUES (13,'13 column 5 group');
INSERT INTO "cols" VALUES (14,'14 column 5 group');
INSERT INTO "cols" VALUES (15,'Planned s0fko');
INSERT INTO "cols" VALUES (16,'In work s0fko');
INSERT INTO "cols" VALUES (17,'Planned test');
INSERT INTO "cols" VALUES (18,'In work test');
INSERT INTO "personal_tasks" VALUES (1,'1 personal task 1 user',1619989200,1621285200,0,1,1);
INSERT INTO "personal_tasks" VALUES (2,'2 personal task 1 user',1619989200,NULL,0,1,1);
INSERT INTO "personal_tasks" VALUES (3,'3 personal task 1 user',NULL,1621285200,0,1,2);
INSERT INTO "personal_tasks" VALUES (4,'4 personal task 2 user',1619989200,1621285200,0,2,15);
INSERT INTO "personal_tasks" VALUES (5,'5 personal task 2 user',1619989200,NULL,0,2,15);
INSERT INTO "personal_tasks" VALUES (6,'6 personal task 2 user',NULL,1621285200,0,2,15);
INSERT INTO "personal_tasks" VALUES (7,'7 personal task 3 user',1619989200,1621285200,0,3,17);
INSERT INTO "personal_tasks" VALUES (8,'8 personal task 3 user',1619989200,NULL,0,3,17);
INSERT INTO "personal_tasks" VALUES (9,'9 personal task 3 user',NULL,1621285200,0,3,18);
INSERT INTO "tasks" VALUES (1,'1 task 1 command',1619989200,1621285200,0,1,3);
INSERT INTO "tasks" VALUES (2,'2 task 1 command',1619989200,NULL,0,2,3);
INSERT INTO "tasks" VALUES (3,'3 task 1 command',NULL,1621285200,0,3,4);
INSERT INTO "tasks" VALUES (4,'4 task 2 command',1619989200,1621285200,0,1,5);
INSERT INTO "tasks" VALUES (5,'5 task 2 command',1619989200,NULL,0,2,6);
INSERT INTO "tasks" VALUES (6,'6 task 2 command',NULL,1621285200,0,3,6);
INSERT INTO "tasks" VALUES (7,'7 task 3 command',1619989200,1621285200,0,1,7);
INSERT INTO "tasks" VALUES (8,'8 task 3 command',1619989200,NULL,0,2,7);
INSERT INTO "tasks" VALUES (9,'9 task 3 command',NULL,1621285200,0,2,7);
INSERT INTO "tasks" VALUES (10,'10 task 1 group',1619989200,1621285200,0,1,9);
INSERT INTO "tasks" VALUES (11,'11 task 1 group',1619989200,NULL,0,2,10);
INSERT INTO "tasks" VALUES (12,'12 task 1 group',NULL,1621285200,0,3,10);
INSERT INTO "tasks" VALUES (13,'13 task 3 group',1619989200,1621285200,0,1,11);
INSERT INTO "tasks" VALUES (14,'14 task 3 group',1619989200,NULL,0,2,11);
INSERT INTO "tasks" VALUES (15,'15 task 3 group',NULL,1621285200,0,3,11);
INSERT INTO "tasks" VALUES (16,'16 task 5 group',1619989200,1621285200,0,1,13);
INSERT INTO "tasks" VALUES (17,'17 task 5 group',1619989200,NULL,0,2,13);
INSERT INTO "tasks" VALUES (18,'18 task 5 group',NULL,1621285200,0,2,14);
INSERT INTO "commands_task" VALUES (1,1,1);
INSERT INTO "commands_task" VALUES (2,1,2);
INSERT INTO "commands_task" VALUES (3,1,1);
INSERT INTO "commands_task" VALUES (4,2,3);
INSERT INTO "commands_task" VALUES (5,2,4);
INSERT INTO "commands_task" VALUES (6,2,4);
INSERT INTO "commands_task" VALUES (7,3,5);
INSERT INTO "commands_task" VALUES (8,3,5);
INSERT INTO "commands_task" VALUES (9,3,6);
INSERT INTO "groups_task" VALUES (10,1);
INSERT INTO "groups_task" VALUES (11,1);
INSERT INTO "groups_task" VALUES (12,1);
INSERT INTO "groups_task" VALUES (13,3);
INSERT INTO "groups_task" VALUES (14,3);
INSERT INTO "groups_task" VALUES (15,3);
INSERT INTO "groups_task" VALUES (16,5);
INSERT INTO "groups_task" VALUES (17,5);
INSERT INTO "groups_task" VALUES (18,5);
INSERT INTO "personal_events" VALUES (1,'1 event 1 user',NULL,0,1);
INSERT INTO "personal_events" VALUES (2,'2 event 1 user',1621285200,0,1);
INSERT INTO "personal_events" VALUES (3,'3 event 2 user',NULL,0,2);
INSERT INTO "personal_events" VALUES (4,'4 event 2 user',1621285200,0,2);
INSERT INTO "personal_events" VALUES (5,'5 event 3 user',NULL,0,3);
INSERT INTO "personal_events" VALUES (6,'6 event 3 user',1621285200,0,3);
INSERT INTO "events" VALUES (1,'1 event 1 command',1652216400);
INSERT INTO "events" VALUES (2,'2 event 1 command',1586120400);
INSERT INTO "events" VALUES (3,'3 event 2 command',1652216400);
INSERT INTO "events" VALUES (4,'4 event 2 command',1586120400);
INSERT INTO "events" VALUES (5,'5 event 3 command',1652216400);
INSERT INTO "events" VALUES (6,'6 event 3 command',1586120400);
INSERT INTO "events" VALUES (7,'7 event 1 group',1652216400);
INSERT INTO "events" VALUES (8,'8 event 1 group',1586120400);
INSERT INTO "events" VALUES (9,'9 event 3 group',1652216400);
INSERT INTO "events" VALUES (10,'10 event 3 group',1586120400);
INSERT INTO "events" VALUES (11,'11 event 5 group',1652216400);
INSERT INTO "events" VALUES (12,'12 event 5 group',1586120400);
INSERT INTO "users_event" VALUES (1,0,2);
INSERT INTO "users_event" VALUES (2,0,2);
INSERT INTO "users_event" VALUES (3,0,1);
INSERT INTO "users_event" VALUES (4,0,1);
INSERT INTO "users_event" VALUES (5,0,1);
INSERT INTO "users_event" VALUES (6,0,2);
INSERT INTO "users_event" VALUES (7,0,1);
INSERT INTO "users_event" VALUES (8,0,2);
INSERT INTO "users_event" VALUES (9,0,2);
INSERT INTO "users_event" VALUES (10,0,3);
INSERT INTO "users_event" VALUES (11,0,1);
INSERT INTO "users_event" VALUES (12,0,2);
INSERT INTO "commands_event" VALUES (1,1);
INSERT INTO "commands_event" VALUES (2,1);
INSERT INTO "commands_event" VALUES (3,2);
INSERT INTO "commands_event" VALUES (4,2);
INSERT INTO "commands_event" VALUES (5,3);
INSERT INTO "commands_event" VALUES (6,3);
INSERT INTO "groups_event" VALUES (7,1);
INSERT INTO "groups_event" VALUES (8,1);
INSERT INTO "groups_event" VALUES (9,3);
INSERT INTO "groups_event" VALUES (10,3);
INSERT INTO "groups_event" VALUES (11,5);
INSERT INTO "groups_event" VALUES (12,5);
COMMIT;
