
CREATE TABLE IF NOT EXISTS `episode_details` (
  `id` int(8) unsigned NOT NULL AUTO_INCREMENT,
  `name_id` int(8) unsigned NOT NULL,
  `url` varchar(255) NOT NULL,
  `episode` varchar(255) NOT NULL,
  `time` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
 ) ENGINE=MyISAM  DEFAULT CHARSET=utf8 ;

 CREATE TABLE IF NOT EXISTS `video_name` (
  `id` int(8) unsigned NOT NULL AUTO_INCREMENT,
  `name_id` int(8) unsigned NOT NULL,
  `name` varchar(255) NOT NULL,
  `md5_name` varchar(255) NOT NULL,
  `video_num` int(4) unsigned NOT NULL,
  PRIMARY KEY (`id`)
 ) ENGINE=MyISAM  DEFAULT CHARSET=utf8 ;