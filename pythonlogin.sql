CREATE DATABASE IF NOT EXISTS `pythonlogin` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `pythonlogin`;
CREATE TABLE IF NOT EXISTS `accounts` (
`id` int(11) NOT NULL AUTO_INCREMENT,
`username` varchar(50) NOT NULL,
`password` varchar(255) NOT NULL,
`email` varchar(100) NOT NULL,
`country` VARCHAR(50) NOT NULL,
`gender` varchar(100) NOT NULL,
`handrec` varchar(8000) NOT NULL,
`countrycode` varchar(5) NOT NULL default '65',
`phoneNO` varchar(20) NOT NULL,
`authyid` varchar(50) NOT NULL,
`logincount` int1(11) NOT NULL,
PRIMARY KEY (`id`),
UNIQUE (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
INSERT INTO `accounts` (`id`, `username`, `password`, `email`, `country`, `gender`, `handrec`, `countrycode`, `phoneNO`, `authyid`, `logincount`) VALUES (1, 'test', 'test', 'mingwenaw@gmail.com', 'test', 'test', '[[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5],[5, 5]]', '65', '97527889', '123', 0);
select * from accounts;
