Truncate Table numbers;
insert into numbers(num1, num2, num3) values (4, 10, 1);
insert into numbers(num1, num2, num3) values (5, 1, 1);
commit;
Select ReadNum2(0);
