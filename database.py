"""内置菜谱数据库"""
from __future__ import annotations

from models import CuisineInfo, Recipe, Step
from recipes_extra import EXTRA_CUISINES, EXTRA_RECIPES


CUISINES: list[CuisineInfo] = [
    CuisineInfo("sichuan", "川菜", "国内", "🌶️", "麻辣鲜香，百菜百味"),
    CuisineInfo("cantonese", "粤菜", "国内", "🦐", "清淡鲜美，讲究原味"),
    CuisineInfo("hunan", "湘菜", "国内", "🔥", "香辣浓郁，口味厚重"),
    CuisineInfo("shandong", "鲁菜", "国内", "🐟", "咸鲜为主，技法多样"),
    CuisineInfo("jiangsu", "苏菜", "国内", "🍲", "清鲜平和，注重刀工"),
    CuisineInfo("japanese", "日本料理", "国外", "🍣", "精致简约，追求本味"),
    CuisineInfo("italian", "意大利菜", "国外", "🍝", "番茄橄榄油，意面披萨"),
    CuisineInfo("french", "法国菜", "国外", "🥐", "精致优雅，酱汁丰富"),
    CuisineInfo("thai", "泰国菜", "国外", "🌿", "酸辣平衡，香料丰富"),
    CuisineInfo("mexican", "墨西哥菜", "国外", "🌮", "玉米辣椒，热情奔放"),
    CuisineInfo("indian", "印度菜", "国外", "🍛", "香料复合，层次丰富"),
    CuisineInfo("korean", "韩国菜", "国外", "🥘", "发酵调味，泡菜文化"),
] + EXTRA_CUISINES


def _steps(items: list[tuple[str, int]]) -> list[Step]:
    return [Step(order=i + 1, description=desc, duration_minutes=dur) for i, (desc, dur) in enumerate(items)]


BUILTIN_RECIPES: list[Recipe] = [
    Recipe(
        id="mapo_tofu",
        name="麻婆豆腐",
        cuisine="sichuan",
        description="经典川菜，豆腐嫩滑，麻辣过瘾",
        ingredients=["嫩豆腐 400g", "牛肉末 100g", "郫县豆瓣 2勺", "花椒粉 1勺", "葱姜蒜 适量", "生抽 1勺", "淀粉水 适量"],
        steps=_steps([
            ("豆腐切2cm方块，入盐水焯1分钟去豆腥，捞出沥干", 3),
            ("热锅冷油，下牛肉末炒散至变色", 3),
            ("加豆瓣酱、姜蒜末炒出红油", 2),
            ("倒入适量热水，下豆腐轻推，中小火烧5分钟", 5),
            ("加生抽调味，分两次勾芡，撒花椒粉和葱花", 2),
        ]),
        difficulty="中等",
        prep_time="25分钟",
    ),
    Recipe(
        id="kungpao_chicken",
        name="宫保鸡丁",
        cuisine="sichuan",
        description="酸甜微辣，花生酥脆",
        ingredients=["鸡胸肉 300g", "花生米 80g", "干辣椒 10个", "花椒 1小把", "黄瓜 半根", "宫保汁：生抽2勺、醋1勺、糖1勺、淀粉1勺"],
        steps=_steps([
            ("鸡丁加料酒、淀粉抓匀腌15分钟", 15),
            ("调宫保汁：生抽、醋、糖、淀粉、少许水混合", 2),
            ("冷油小火炸花生米至酥脆，捞出", 5),
            ("大火快炒鸡丁至变色盛出", 3),
            ("余油爆香干辣椒、花椒，下黄瓜丁、鸡丁", 2),
            ("倒入宫保汁和花生米，大火翻匀出锅", 1),
        ]),
        difficulty="中等",
        prep_time="35分钟",
    ),
    Recipe(
        id="steamed_fish",
        name="清蒸鲈鱼",
        cuisine="cantonese",
        description="粤菜代表，鱼肉鲜嫩，原汁原味",
        ingredients=["鲈鱼 1条(约500g)", "姜葱 适量", "蒸鱼豉油 3勺", "料酒 1勺", "食用油 2勺"],
        steps=_steps([
            ("鱼处理干净，两面划刀，抹料酒，鱼身垫姜片", 5),
            ("水开后大火蒸8-10分钟（视鱼大小）", 10),
            ("取出倒掉盘中腥水，铺葱丝", 1),
            ("淋蒸鱼豉油，浇上热油激香", 1),
        ]),
        difficulty="简单",
        prep_time="20分钟",
    ),
    Recipe(
        id="char_siu",
        name="叉烧",
        cuisine="cantonese",
        description="蜜汁叉烧，色泽红亮",
        ingredients=["梅花肉 500g", "叉烧酱 3勺", "蜂蜜 2勺", "生抽 2勺", "料酒 1勺", "姜蒜 适量"],
        steps=_steps([
            ("肉切条，叉烧酱、蜂蜜、生抽、料酒、姜蒜腌制4小时以上", 240),
            ("烤箱200°C预热，肉铺烤网，下层接烤盘", 10),
            ("烤20分钟后刷腌料，再烤15-20分钟至表面焦香", 35),
            ("取出稍凉切片", 5),
        ]),
        difficulty="中等",
        prep_time="4小时30分钟",
    ),
    Recipe(
        id="duojiao_fish_head",
        name="剁椒鱼头",
        cuisine="hunan",
        description="湘菜名菜，鲜辣开胃",
        ingredients=["胖头鱼头 1个", "剁椒 200g", "姜葱 适量", "蒸鱼豉油 2勺", "料酒 1勺", "食用油 3勺"],
        steps=_steps([
            ("鱼头对半劈开洗净，抹料酒，铺姜片", 5),
            ("铺满剁椒，淋少许蒸鱼豉油", 2),
            ("大火蒸12-15分钟", 15),
            ("撒葱花，浇热油", 1),
        ]),
        difficulty="中等",
        prep_time="25分钟",
    ),
    Recipe(
        id="sweet_sour_pork",
        name="糖醋里脊",
        cuisine="shandong",
        description="外酥里嫩，酸甜适口",
        ingredients=["猪里脊 300g", "鸡蛋 1个", "淀粉 适量", "番茄酱 3勺", "白糖 2勺", "白醋 1勺"],
        steps=_steps([
            ("里脊切条，加盐、料酒腌10分钟", 10),
            ("裹蛋液和淀粉，下180°C油锅炸至金黄", 8),
            ("复炸30秒更酥脆", 1),
            ("另锅炒番茄酱、糖、醋、少许水成糖醋汁", 3),
            ("倒入里脊快速裹匀出锅", 1),
        ]),
        difficulty="中等",
        prep_time="30分钟",
    ),
    Recipe(
        id="squirrel_fish",
        name="松鼠桂鱼",
        cuisine="jiangsu",
        description="苏菜经典，造型美观，酸甜酥脆",
        ingredients=["桂鱼 1条", "番茄酱 4勺", "白糖 3勺", "白醋 2勺", "淀粉 适量", "青豆玉米 装饰"],
        steps=_steps([
            ("鱼去骨，切花刀，拍干淀粉", 15),
            ("油温180°C炸至定型呈松鼠状", 8),
            ("调糖醋汁：番茄酱、糖、醋、水、少许淀粉", 3),
            ("浇汁于鱼身，撒青豆玉米", 1),
        ]),
        difficulty="困难",
        prep_time="45分钟",
    ),
    Recipe(
        id="sushi_roll",
        name="寿司卷",
        cuisine="japanese",
        description="经典手卷寿司，醋饭与海鲜的完美结合",
        ingredients=["寿司米 2杯", "寿司醋 3勺", "海苔 4张", "黄瓜 1根", "蟹棒 4根", "三文鱼 100g"],
        steps=_steps([
            ("寿司米煮熟，趁热拌寿司醋，扇凉", 30),
            ("海苔铺竹帘，铺薄层米饭，留边", 5),
            ("放黄瓜条、蟹棒、三文鱼，卷紧", 5),
            ("切刀沾水，切成8段", 3),
        ]),
        difficulty="中等",
        prep_time="45分钟",
    ),
    Recipe(
        id="ramen",
        name="日式拉面",
        cuisine="japanese",
        description="浓郁豚骨汤底，劲道面条",
        ingredients=["拉面 2份", "猪骨 500g", "味噌/酱油 适量", "溏心蛋 2个", "叉烧 4片", "海苔 2片", "葱花 适量"],
        steps=_steps([
            ("猪骨焯水后小火炖2小时成浓汤", 120),
            ("汤中加味噌或酱油调味", 5),
            ("拉面煮熟，过冷水更劲道", 4),
            ("碗中放面、汤、叉烧、溏心蛋、海苔、葱花", 3),
        ]),
        difficulty="困难",
        prep_time="2小时30分钟",
    ),
    Recipe(
        id="carbonara",
        name="卡博纳拉意面",
        cuisine="italian",
        description="罗马经典，蛋黄奶酪包裹意面",
        ingredients=["意面 200g", "培根 100g", "蛋黄 2个", "帕玛森芝士 50g", "黑胡椒 适量"],
        steps=_steps([
            ("意面按包装说明煮至al dente，留1杯面汤", 10),
            ("培根切条，干锅煎至酥脆", 5),
            ("蛋黄、芝士、黑胡椒混合成酱", 2),
            ("面与培根混合，离火加蛋黄酱快速搅拌，加面汤调节", 2),
        ]),
        difficulty="简单",
        prep_time="20分钟",
    ),
    Recipe(
        id="margherita_pizza",
        name="玛格丽特披萨",
        cuisine="italian",
        description="那不勒斯经典，番茄-mozzarella-罗勒",
        ingredients=["披萨面团 1份", "番茄沙司 3勺", "马苏里拉 150g", "新鲜罗勒 若干", "橄榄油 适量"],
        steps=_steps([
            ("面团擀成圆饼，边缘稍厚", 10),
            ("涂番茄沙司，铺马苏里拉", 3),
            ("250°C烤10-12分钟至边缘焦斑", 12),
            ("出炉铺罗勒，淋橄榄油", 1),
        ]),
        difficulty="中等",
        prep_time="30分钟",
    ),
    Recipe(
        id="beef_bourguignon",
        name="勃艮第红酒炖牛肉",
        cuisine="french",
        description="法式慢炖经典，红酒与牛肉的深度融合",
        ingredients=["牛腩 600g", "红酒 300ml", "洋葱 2个", "胡萝卜 2根", "蘑菇 200g", "百里香 2枝", "牛肉高汤 500ml"],
        steps=_steps([
            ("牛肉切块，拍干，煎至表面焦褐", 10),
            ("炒洋葱、胡萝卜至软，加红酒煮减", 15),
            ("加牛肉、高汤、百里香，小火炖2小时", 120),
            ("另炒蘑菇，最后15分钟加入", 15),
        ]),
        difficulty="困难",
        prep_time="3小时",
    ),
    Recipe(
        id="tom_yum",
        name="冬阴功汤",
        cuisine="thai",
        description="泰国国汤，酸辣鲜香",
        ingredients=["大虾 8只", "香茅 2根", "南姜 3片", "柠檬叶 5片", "冬阴功酱 2勺", "椰浆 100ml", "鱼露 1勺", "lime 1个"],
        steps=_steps([
            ("水开下香茅、南姜、柠檬叶煮5分钟", 5),
            ("加冬阴功酱、虾、蘑菇", 5),
            ("加椰浆、鱼露，挤青柠，勿久煮", 3),
        ]),
        difficulty="中等",
        prep_time="20分钟",
    ),
    Recipe(
        id="pad_thai",
        name="泰式炒河粉",
        cuisine="thai",
        description="泰国街头经典，甜酸平衡",
        ingredients=["河粉 200g", "虾 100g", "豆芽 100g", "花生碎 2勺", "罗望子酱 2勺", "鱼露 1勺", "棕榈糖 1勺", "鸡蛋 1个"],
        steps=_steps([
            ("河粉泡软沥干", 15),
            ("热油炒蛋划散，加虾", 3),
            ("下河粉、罗望子酱、鱼露、糖快炒", 4),
            ("加豆芽、花生碎，挤青柠", 2),
        ]),
        difficulty="中等",
        prep_time="25分钟",
    ),
    Recipe(
        id="tacos",
        name="墨西哥 tacos",
        cuisine="mexican",
        description="软/硬玉米饼包裹丰富馅料",
        ingredients=["玉米饼 6张", "牛肉末 300g", " taco 调料 2勺", "生菜 适量", "番茄 1个", "酸奶油 适量", "芝士 适量"],
        steps=_steps([
            ("牛肉末加 taco 调料炒散至熟透", 8),
            ("番茄切丁，生菜切丝", 5),
            ("玉米饼加热", 2),
            ("饼上铺肉、生菜、番茄、芝士、酸奶油", 3),
        ]),
        difficulty="简单",
        prep_time="20分钟",
    ),
    Recipe(
        id="butter_chicken",
        name="黄油鸡",
        cuisine="indian",
        description="印度北部经典，奶油番茄咖喱",
        ingredients=["鸡腿肉 400g", "酸奶 100g", "姜蒜 适量", "印度综合香料 2勺", "番茄 3个", "黄油 50g", "奶油 100ml"],
        steps=_steps([
            ("鸡肉用酸奶、姜蒜、香料腌1小时", 60),
            ("番茄打成酱，黄油炒香剩余香料", 5),
            ("加番茄酱煮10分钟，加鸡肉炖20分钟", 20),
            ("加奶油，小火5分钟", 5),
        ]),
        difficulty="中等",
        prep_time="1小时40分钟",
    ),
    Recipe(
        id="kimchi_jjigae",
        name="泡菜锅",
        cuisine="korean",
        description="韩国家常锅物，酸辣暖身",
        ingredients=["老泡菜 300g", "五花肉 150g", "豆腐 1块", "洋葱 半个", "韩式辣酱 1勺", "大葱 1根", "水/高汤 500ml"],
        steps=_steps([
            ("五花肉切片，泡菜切段", 5),
            ("锅炒五花肉出油，加泡菜炒2分钟", 5),
            ("加水/高汤、辣酱，煮10分钟", 10),
            ("加豆腐、洋葱，再煮5分钟，撒葱段", 5),
        ]),
        difficulty="简单",
        prep_time="30分钟",
    ),
    Recipe(
        id="bibimbap",
        name="石锅拌饭",
        cuisine="korean",
        description="五色蔬菜配辣酱，营养均衡",
        ingredients=["米饭 2碗", "牛肉 100g", "菠菜、豆芽、胡萝卜、香菇 各50g", "鸡蛋 2个", "韩式辣酱 2勺", " sesame油 1勺"],
        steps=_steps([
            ("各蔬菜分别焯水或快炒，牛肉加酱油腌后炒", 15),
            ("石锅刷油，铺米饭，摆蔬菜、牛肉", 5),
            ("煎太阳蛋，放顶部", 3),
            ("加辣酱、香油，上桌搅拌", 1),
        ]),
        difficulty="中等",
        prep_time="35分钟",
    ),
] + EXTRA_RECIPES


def get_cuisines() -> list[CuisineInfo]:
    return CUISINES.copy()


def get_cuisines_by_region(region: str) -> list[CuisineInfo]:
    return [c for c in CUISINES if c.region == region]


def get_recipes_by_cuisine(cuisine_id: str) -> list[Recipe]:
    return [r for r in BUILTIN_RECIPES if r.cuisine == cuisine_id]


def get_recipe_by_id(recipe_id: str) -> Recipe | None:
    for recipe in BUILTIN_RECIPES:
        if recipe.id == recipe_id:
            return recipe
    return None


def get_cuisine_by_id(cuisine_id: str) -> CuisineInfo | None:
    for cuisine in CUISINES:
        if cuisine.id == cuisine_id:
            return cuisine
    return None


def search_recipes(keyword: str, difficulty: str = "") -> list[Recipe]:
    """按菜名、描述、食材搜索菜谱，可按难度筛选"""
    keyword = keyword.strip().lower()
    difficulty = difficulty.strip()
    if not keyword:
        return []
    results: list[Recipe] = []
    for recipe in BUILTIN_RECIPES:
        if difficulty and recipe.difficulty != difficulty:
            continue
        haystack = " ".join([
            recipe.name,
            recipe.description,
            " ".join(recipe.ingredients),
        ]).lower()
        if keyword in haystack:
            results.append(recipe)
    return results
