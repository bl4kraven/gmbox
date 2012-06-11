#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = '''gmbox常量文件

这个文件定义了gmbox核心库使用的常量，可能需要定时更新。
'''

ARITST = {
    "男歌手" : "male",
    "女歌手" : "female",
    "男女对唱" : "dual",
    "组合" : "group",
    "合唱" : "choral"
}

GENRES = {
    "摇滚" : "rnr",
    "民谣" : "fol",
    "民族" : "nat",
    "流行" : "pop",
    "影视" : "mnt",
    "乡村" : "cnt",
    "古典" : "cls",
    "说唱" : "hnr",
    "拉丁" : "lat",
    "灵歌" : "sol",
    "爵士蓝调" : "jnb",
    "电子乐" : "elc",
    "节奏蓝调" : "rnb",
    "轻音乐" : "esl",
    "其它" : "-rnr,-fol,-nat,-pop,-mnt,-cnt,-cls,-hnr,-lat,-sol,-jnb,-elc,-rnb,-esl,other"
}

LANGS = {
    "国语" : "zh-cmn",
    "粤语" : "zh-yue",
    "英语" : "en",
    "日语" : "ja",
    "韩语" : "ko",
    "意大利语" : "it",
    "德语" : "de",
    "法语" : "fr",
    "其它" : "-zh-cmn,-zh-yue,-en,-ja,-ko,-it,-de,-fr,other"
}

CHARTLISTING_DIR = [
# 最新音乐
    #("华语新歌", "chinese_new_songs_cn"),
    #("欧美新歌", "ea_new_songs_cn"),
    ("华语最新专辑", "chinese_new-release_albums_cn"),
    ("欧美最新专辑", "ea_new-release_albums_cn"),
    ("最新专辑", "new-release_albums_cn"),
# 华语
    ("华语热歌", "chinese_songs_cn"),
    ("华语新歌", "chinese_new_songs_cn"),
    ("华语热碟", "chinese_albums_cn"),
    ("华语歌手", "chinese_artists_cn"),
# 欧美
    ("欧美热歌", "ea_songs_cn"),
    ("欧美新歌", "ea_new_songs_cn"),
    ("欧美热碟", "ea_albums_cn"),
    ("欧美歌手", "ea_artists_cn"),
# 日韩
    ("日韩热歌", "jk_songs_cn"),
    ("日韩热碟", "jk_albums_cn"),
    ("日韩歌手", "jk_artists_cn"),
# 流行
    ("流行热歌", "pop_songs_cn"),
    ("流行新碟", "pop_new_albums_cn"),
    ("流行热碟", "pop_albums_cn"),
# 摇滚
    ("摇滚热歌", "rock_songs_cn"),
    ("摇滚新碟", "rock_new_albums_cn"),
    ("摇滚热碟", "rock_albums_cn"),
# 嘻哈
    ("嘻哈热歌", "hip-hop_songs_cn"),
    ("嘻哈新碟", "hip-hop_new_albums_cn"),
    ("嘻哈热碟", "hip-hop_albums_cn"),
# 影视
    ("影视热歌", "soundtrack_songs_cn"),
    ("影视新碟", "soundtrack_new_albums_cn"),
    ("影视热碟", "soundtrack_albums_cn"),
# 民族
    ("民族热歌", "ethnic_songs_cn"),
    ("民族热碟", "ethnic_albums_cn"),
# 拉丁
    ("拉丁热歌", "latin_songs_cn"),
    ("拉丁热碟", "latin_albums_cn"),
# R&B
    ("R&B热歌", "rnb_songs_cn"),
    ("R&B热碟", "rnb_albums_cn"),
# 乡村
    ("乡村热歌", "country_songs_cn"),
    ("乡村热碟", "country_albums_cn"),
# 民谣
    ("民谣热歌", "folk_songs_cn"),
    ("民谣热碟", "folk_albums_cn"),
# 灵歌
    ("灵歌热歌", "soul_songs_cn"),
    ("灵歌热碟", "soul_albums_cn"),
# 轻音乐
    ("轻音乐热歌", "easy-listening_songs_cn"),
    ("轻音乐热碟", "easy-listening_albums_cn"),
# 爵士蓝调
    ("爵士蓝调热歌", "jnb_songs_cn"),
    ("爵士蓝调热碟", "jnb_albums_cn")
]

TAG_DIR = [
# 情绪
    "压抑", "平静", "快乐", "放松", "忧伤",
    "宣泄", "细腻", "发泄", "感动", "寂寞",
    "温暖", "失落", "忧郁", "思念", "悲伤",
    "失恋", "痛苦",
# 乐器
    "二胡", "琵琶", "口哨", "小提琴", "古筝",
    "钢琴", "民乐", "吉他",
# 节奏旋律
    "明快", "优美", "流畅", "婉转", "悠扬",
    "简单", "轻盈", "动感", "轻快", "舒缓",
# 场景
    "汽车", "夏天", "旅行", "阳光", "雨天",
    "春天", "冬天", "午后", "夜晚", "独自",
    "工作",
# 风格
    "中国风", "乡村", "儿歌", "前卫", "古典",
    "另类", "嘻哈", "宗教", "戏剧", "拉丁",
    "摇滚", "有声书", "民族", "民谣", "流行",
    "演讲", "灵歌", "爵士蓝调", "电子", "硬摇滚",
    "脱口秀", "舞曲", "节奏布鲁斯", "节庆音乐", "蓝调",
    "语言艺术", "说唱", "轻音乐", "迷幻", "金属",
    "革命歌曲", "音乐剧",
# 主题
    "情歌", "影视", "公益", "奥运", "励志",
    "广告", "游戏",
# 音色
    "高亢", "轻柔", "沧桑", "甜美", "聆听",
    "吟唱", "明亮", "清澈", "慵懒", "沙哑",
    "温柔", "空灵", "磁性", "粗犷", "低沉",
    "柔美"
]
