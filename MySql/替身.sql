create table emp(
	id int comment '编号',
	workno varchar(10) comment '员工工号',
	name varchar(10) comment '员工姓名',
	gender char(1) comment '性别',
	age tinyint unsigned comment '年龄',
	idcard char(18) comment '身份证号',
	entrydate date comment '入职时间'
)comment '员工信息表';

ALTER TABLE emp ADD nickname varchar(20) comment '昵称';

ALTER TABLE emp CHANGE nickname username varchar(30);

ALTER TABLE emp DROP username;





