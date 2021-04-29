BEGIN TRANSACTION;
INSERT INTO "users" VALUES (1,'mrs','b21dabb4c22d87c7e22f179206f3fa06efe0e6379df60ee5cfca87bea6efd236','Сашко','2,1'); --Пароль mrs
INSERT INTO "users" VALUES (2,'s0fko','a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3','Софійка',NULL); --Пароль 123
INSERT INTO "commands" VALUES (1,'Command 1',1,NULL);
INSERT INTO "commands" VALUES (2,'Command 2',2,NULL);
INSERT INTO "commands_user" VALUES (1,1);
INSERT INTO "commands_user" VALUES (1,2);
INSERT INTO "commands_user" VALUES (2,1);
INSERT INTO "commands_user" VALUES (2,2);
INSERT INTO "cols" VALUES (1,'Розподілено');
INSERT INTO "cols" VALUES (2,'Виконується');
INSERT INTO "personal_tasks" VALUES (1,'Оце таке чудове перше завдання',NULL,NULL,0,1,1);
INSERT INTO "personal_tasks" VALUES (2,'Завдання 2',NULL,NULL,0,1,1);
INSERT INTO "personal_tasks" VALUES (3,'Поїсти',NULL,NULL,0,1,2);
COMMIT;
