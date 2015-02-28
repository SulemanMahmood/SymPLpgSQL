Truncate Table numbers;
insert into numbers(num1, num2, num3) values (4, 10, 0);
insert into numbers(num1, num2, num3) values (5, 2, 1);
commit;
Select ReadNum2(0);
