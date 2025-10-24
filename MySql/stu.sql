/*
Navicat MySQL Data Transfer

Source Server         : f
Source Server Version : 50553
Source Host           : localhost:3306
Source Database       : stu

Target Server Type    : MYSQL
Target Server Version : 50553
File Encoding         : 65001

Date: 2025-03-11 09:36:46
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for score
-- ----------------------------
DROP TABLE IF EXISTS `score`;
CREATE TABLE `score` (
  `id` char(10) NOT NULL DEFAULT '',
  `stu_id` int(10) NOT NULL,
  `c_class` varchar(20) DEFAULT NULL,
  `grade` int(10) DEFAULT NULL,
  UNIQUE KEY `id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='成绩单';

-- ----------------------------
-- Records of score
-- ----------------------------
INSERT INTO `score` VALUES ('1', '901', '计算机', '98');
INSERT INTO `score` VALUES ('2', '901', '英语', '80');
INSERT INTO `score` VALUES ('3', '902', '计算机', '65');
INSERT INTO `score` VALUES ('4', '902', '中文', '65');
INSERT INTO `score` VALUES ('5', '903', '中文', '95');
INSERT INTO `score` VALUES ('6', '904', '计算机', '70');
INSERT INTO `score` VALUES ('7', '904', '英语', '92');
INSERT INTO `score` VALUES ('8', '905', '英语', '94');
INSERT INTO `score` VALUES ('9', '906', '计算机', '90');
INSERT INTO `score` VALUES ('10', '906', '英语', '85');

-- ----------------------------
-- Table structure for student
-- ----------------------------
DROP TABLE IF EXISTS `student`;
CREATE TABLE `student` (
  `id` int(10) NOT NULL,
  `uname` varchar(20) NOT NULL,
  `sex` varchar(4) DEFAULT NULL,
  `birth` year(4) DEFAULT NULL,
  `department` varchar(20) NOT NULL,
  `address` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='学生表';

-- ----------------------------
-- Records of student
-- ----------------------------
INSERT INTO `student` VALUES ('901', '张老大', '男', '1985', '计算机系', '北京省海淀区');
INSERT INTO `student` VALUES ('902', '张老二', '男', '1986', '中文系', '北京市昌平区');
INSERT INTO `student` VALUES ('903', '张三', '女', '1990', '中文系', '湖南省永州市');
INSERT INTO `student` VALUES ('904', '李四', '男', '1990', '英语系', '辽宁省阜新市');
INSERT INTO `student` VALUES ('905', '王五', '女', '1991', '英语系', '福建省厦门市');
INSERT INTO `student` VALUES ('906', '王六', '男', '1988', '计算机系', '湖南省衡阳市');
