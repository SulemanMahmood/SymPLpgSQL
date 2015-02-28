Truncate Table numbers;
insert into numbers(num1, num2, num3) values (3, 1, 0);
insert into numbers(num1, num2, num3) values (4, 3, 0);
commit;
Select ReadNum2(0);
