# -*- coding: utf-8 -*-
# core.py (self-contained)
"""
缂傚倸鍊风欢锟犲窗閺嶃劍娅犲ù鐘差儐閸嬧晜绻濋棃娑卞剱闁稿顑夐弻娑㈩敃閵堝懏鐏佹繝銏㈡嚀椤戝鎮￠锕€鐐婄憸宥夊几閿斿墽纾奸柛娆惷畵鍡橆殽閻愭彃顒㈢紒缁樼箞瀹曟帒顫濋鐔轰紜闂傚倷鑳堕…鍫㈡崲閹扮増鍋嬮柛鈩冪☉閸ㄥ倿骞栧ǎ顒€濡奸柡瀣╃窔閺屻劌鈹戦崱妯烘闂傚鍓﹂崜娆撯€﹂崸妤佸殝闁汇垻鏁搁崣婵嬫⒒娴ｇ绾х紒顔肩焷閻忔帡姊洪悙钘夊姤婵炲懏娲熷畷鎴﹀Ψ閳哄倻鍘介梺闈涱焾閸庨亶顢旈埡鍛厽闁靛牆鎳庨顓㈡煙椤旇棄鈻曟鐐茬Ч椤㈡瑩骞嗚閸樺嘲鈹戦悙鏉戠仸闁瑰憡鎸冲畷鎴﹀箻缂佹鍘告繛杈剧秬椤绱為幋锔界厵妞ゆ柨銈搁崣鍕偓瑙勬礃绾板秹鏁嶉幇顓熷濞撴凹鍨槐妯衡攽閻愭潙鐏﹂柟灏栨櫆缁傚秴鈹戠€ｎ亜鍤戦梺鍛婂姀閺呮繈銆呴悜鑺ョ厱妞ゆ劧绲剧粈鈧┑鐐叉嫅缁绘繈寮?
闂備浇顕уù鐑藉极閹间礁绠犻柟鎯у殺閸ャ劎绡€婵﹩鍓涢宀勬⒑瑜版帒浜板ù婊呭仦濞煎寮埀顒傛崲濞戙垹绠婚柧蹇ｅ亜濞呫倕鈹戦悙鍙夊櫤鐎光偓閹间礁绠氶柛鎰靛枛缁€瀣亜閹扳晛鐏柣锔肩秮濮婄儤娼幍顔煎濠电姰鍨洪敃銏ょ嵁閸愵喖鍗抽柕蹇婂墲濞呮牠鏌ｈ箛鏇炰哗闁稿鍔栧?main.py 闂備浇宕垫慨鎾敄閸涙潙鐤ù鍏兼綑閺嬩線鏌曢崼婵愭Ц鏉╂繈姊虹粙鎸庢拱缂佸甯￠弫鎾诲Ψ閳哄倵鎷婚梺鎼炲劵缁茶姤绂嶆ィ鍐┾拺缂佸娉曠粻鐑樼箾婢跺娲撮柟?.py 婵犵數鍋為幐鑽ゅ枈瀹ュ洦宕查柛鈩冪懅閻鏌涢埄鍐槈鏉?
"""
from typing import Dict, List, Tuple, Optional, TypeAlias, Any, Set
import math
import re

# ====== 闂傚倸鍊风欢锟犲磻閸涱収娼╅柕濞炬櫅閺?3D 濠电姷顣藉Σ鍛村垂椤忓牆鐒垫い鎺嗗亾缁剧虎鍙冮崺鈧い鎺戝閺佽京绱掔€ｎ亶妯€妞ゃ垺锕㈤幃娆撴濞戣鲸鍠橀梻浣筋嚙缁绘帡宕戦悢鐓庣；闁绘劕鎼悞鍨亜閹搭厼澧柛濠傤煼閹兘濮€閳藉棙顔旈梺缁樺姌鐏忔瑩鏁嶅鍡欘洸婵炴垯鍨洪悡銉︾箾閹寸儐鐒藉褎姊荤槐鎺旂磼濡搫鎽靛Δ鐘靛仦閸旀牠骞忛崨瀛樺仭闁哄顑欏Σ濠氭⒒娴ｅ憡鍟為柣鐔讳含瀵板﹪鎳栭埡鍐暥婵犮垼鍩栭崝鏇㈡儗濡や焦鍙忔俊銈傚亾闁绘绻掔划?======
Point3D: TypeAlias = Tuple[float, float, float]
Seg3D: TypeAlias = List[Point3D]
Model3DData: TypeAlias = Dict[str, Seg3D]


def _model_sort_key(value: Any) -> Tuple[Tuple[Tuple[int, Any], ...], str]:
    """Natural drawing order: 09 before 10, J1-9 before J1-10."""
    text = str(value)
    parts = re.split(r"(\d+)", text)
    key = tuple(
        (0, int(part)) if part.isdigit() else (1, part.lower())
        for part in parts
    )
    return key, text.lower()


def base_id(rid) -> str:
    """
    婵?'508_2' / '1310_1' / '508' 婵犵數鍋為崹鍫曞箹閳哄懎鍌ㄩ柛濠勫枂娴滅懓銆掑锝呬壕閻庤娲╃紞浣割嚕閸婄噥妲鹃梺鍝ュ亼閸旀垿寮诲☉銏犵婵犻潧娴傚Λ锟犳⒑鐠囨彃鐦ㄩ柛銊ㄤ含缁骞掗弮鈧畷澶愭煕濠靛棗顏╅柍璇茬箻濮?
    缂傚倸鍊搁崐鐑芥嚄閸洖绐楃€广儱娲ㄩ崡姘舵煙缂併垹鏋涚紒鐘劦閺屽秷顧侀柛鎾跺枎椤曪綁宕归銏㈢獮闁诲函缍嗛崑鍡涘储閹扮増鍊甸柣鎰嚀閳ь剚绻勭槐鎾愁潩椤撴繄绠氬銈嗘尪閸ㄦ椽宕?ID 闂傚倷鐒﹂惇褰掑礉瀹€鈧埀顒佸嚬閸撴岸寮查崼鏇熷亹闁汇垻鏁搁敍婵嬫⒑闁偛鑻晶瀵糕偓娈垮枛閻栧吋淇婇悜鑺ユ櫆闁告挆鍐帗闂傚倷鐒︾€笛呯矙閹达附鍎楅柛灞剧☉椤曢亶鏌嶉崫鍕櫣缂佲偓閸屾壕鍋撻獮鍨姎婵☆偅顨嗛崕顐︽⒒娴ｅ憡鍟為柤瑙勫劤闇夊瀣椤洟鏌熺€电校闁哥姴妫濋弻娑㈠焺閸愨晝顦紓浣插亾閻庯綆浜栧Σ?ID 婵犵數鍋為崹鍫曞箰閹绢喖纾婚柟鍓х帛閳锋垶銇勯弬鎸庢儓濠碘€炽偢閺屾盯濡搁妷鈺佸及婵?
    """
    return str(rid).split("_", 1)[0]


def node_id_base(rid) -> str:
    """Build a numeric node-ID prefix without losing a duplicate-instance suffix."""
    return str(rid).replace("_", "")

def _collect_endpoints(segdict: Model3DData) -> List[Point3D]:
    pts: List[Point3D] = []
    for seg in segdict.values():
        if seg and len(seg) >= 2:
            pts.append(seg[0]); pts.append(seg[1])
    return pts

def center_props(front3d: Model3DData, right3d: Model3DData):
    """闂備礁鎼ˇ顐﹀疾濠婂牆钃熼柕濞垮剭?((x_center, y_center, 0), z_min)"""
    all_pts = _collect_endpoints(front3d) + _collect_endpoints(right3d)
    if not all_pts: return (0.0, 0.0, 0.0), 0.0
    xs = [p[0] for p in all_pts]; ys = [p[1] for p in all_pts]; zs = [p[2] for p in all_pts]
    x_center = (min(xs) + max(xs)) / 2.0
    y_center = (min(ys) + max(ys)) / 2.0
    z_min = min(zs)
    return (x_center, y_center, 0.0), z_min

def translate_model(front3d: Model3DData, right3d: Model3DData, translation_target: Tuple[float,float,float]):
    dx, dy, dz = -translation_target[0], -translation_target[1], -translation_target[2]
    def _apply(d: Model3DData) -> Model3DData:
        return {gid: [(p[0]+dx, p[1]+dy, p[2]+dz) for p in seg] for gid, seg in d.items()}
    return _apply(front3d), _apply(right3d)

def top_xmid_and_range(horiz_dict: Dict[str, List[Tuple[float, float]]],
                       preferred_key: Optional[str] = None,
                       y_top: Optional[float] = None,
                       tol_abs: Optional[float] = None,
                       tol_ratio: float = 0.05,
                       y_eps: float = 1e-6):
    if not horiz_dict: return None, None, None
    def _seg_info(seg):
        (x1, y1), (x2, y2) = seg[0], seg[1]
        length = abs(x2 - x1); y_mean = (y1 + y2) / 2.0
        return x1, y1, x2, y2, length, y_mean
    chosen_key, seg = None, None
    if preferred_key and preferred_key in horiz_dict:
        chosen_key, seg = preferred_key, horiz_dict[preferred_key]
    if seg is None and (y_top is not None):
        cand = []
        for k, s in horiz_dict.items():
            if not s or len(s) < 2: continue
            x1,y1,x2,y2,L,ym = _seg_info(s)
            if abs(y1 - y_top) <= y_eps and abs(y2 - y_top) <= y_eps:
                cand.append((L, k, s))
        if cand:
            cand.sort(reverse=True); _, chosen_key, seg = cand[0]
    if seg is None:
        best = None
        for k,s in horiz_dict.items():
            if not s or len(s) < 2: continue
            x1,y1,x2,y2,L,ym = _seg_info(s)
            if (best is None) or (ym > best[0]): best = (ym, k, s)
        if best: _, chosen_key, seg = best
    if seg is None or len(seg) < 2: return None, None, None
    x1,y1,x2,y2,seg_len,_ = _seg_info(seg)
    x_mid = (x1 + x2) / 2.0
    tol = float(tol_abs) if (tol_abs is not None) else (abs(seg_len) * (tol_ratio if tol_ratio is not None else 0.05) or 1.0)
    x_range = (x_mid - tol, x_mid + tol)
    meta = {"key": chosen_key, "seg_len": seg_len, "y": (y1+y2)/2.0, "tol": tol, "endpoints": [(x1,y1),(x2,y2)]}
    return x_mid, x_range, meta

# ====== X 闂傚倷鐒﹂幃鍫曞礉瀹€鍕垫晞闁糕剝绋掗崐鍨亜閺嶃劎銆掓い鈺冨厴閺屾盯骞橀懠璺哄帯闂佽鏋荤紞浣割潖?======
def select_x_type(rest_dict: Dict[str, List[Tuple[float, float]]], x_range: Tuple[float, float]) -> Dict[str, List[Tuple[float, float]]]:
    if not rest_dict or not x_range: return {}
    lo, hi = x_range; out = {}
    for k, seg in rest_dict.items():
        if not seg or len(seg) < 2: continue
        (x1,y1),(x2,y2) = seg[0],seg[1]
        x_mid = (x1 + x2) / 2.0
        if lo <= x_mid <= hi: out[str(k)] = [tuple(seg[0]), tuple(seg[1])]
    return out

# ====== 闂傚倷绀佸﹢閬嶁€﹂崼銉嬪洭骞嶉鐟颁壕闁割煈鍋呴惃鎴︽煃瑜滈崜婵嬶綖婢跺苯鏋堢€广儱鎷嬮悞浠嬫倶閻愭彃鈷旀い鈺冨厴閹銈﹂幐搴哗闂佸搫顦划娆忣潖婵犳艾鐒垫い鎺戝€瑰畷澶愭煏婵炑冩噽椤︻偊姊绘担濮愨偓鈧柛?======
def scale_by_member(final_coords_map: Dict[str, List[Tuple[float, float, float]]], target_id: str, real_length: float):
    p1, p2 = final_coords_map.get(target_id, (None, None))
    if p1 is None or p2 is None: raise KeyError(f"member id {target_id} not found")
    L = math.sqrt(sum((a-b)**2 for a,b in zip(p1, p2)))
    if L < 1e-9: raise ValueError("selected member is too short")
    s = real_length / L
    return {mid: [(p[0]*s, p[1]*s, p[2]*s) for p in seg] for mid, seg in final_coords_map.items()}


# ====== Loader ======
# loader.py
import re
from typing import Dict, List, Tuple, TypeAlias

Coord: TypeAlias = Tuple[float, float]
CoordDict: TypeAlias = Dict[str, List[Coord]]

# 闂備浇宕甸崰鎰版偡鏉堚晛绶ゅΔ锝呭暞閸?block 闂佽崵鍠愮划蹇涘春閸ヮ剙鍨傞柛锔诲幗椤洟鏌ㄩ悢鍝勑ｉ柡鍜佸墯閹便劌鈹戦崶鈺冩綁ordinatesFront_data={ id:[(x1,y1),(x2,y2)], ... }
_BLOCK_RE = re.compile(
    r"coordinates(?P<name>Front|Overhead)_data\s*=\s*\{(?P<body>.*?)\}",
    re.IGNORECASE | re.DOTALL,
)
_PAIR_RE = re.compile(
    r"(?P<id>[0-9A-Za-z_]+)\s*:\s*\[\s*\(\s*(?P<x1>[-+0-9.eE]+)\s*,\s*(?P<y1>[-+0-9.eE]+)\s*\)\s*,\s*\(\s*(?P<x2>[-+0-9.eE]+)\s*,\s*(?P<y2>[-+0-9.eE]+)\s*\)\s*\]",
    re.IGNORECASE,
)

# 闂備浇宕甸崰鎰版偡鏉堚晛绶ゅΔ锝呭暞閸婇潧霉閻樺樊鍎忛柣蹇氭珪缁绘繃绻濋崒姘闂佽楠搁…鐑藉蓟閵堝浼犻柛鏇ㄥ亐閸嬫捇鎮界粙璺ㄥ姦濡炪倖甯婇懗鍓佺不閹剧粯鐓犻柛娑橈攻缁跺弶銇勯弴顏嗙К缂佺姵鐩俊鐤槾闁绘稏鍎茬换?front/right 闂傚倷绀侀幉锛勬暜閳哄懎纾婚柛鏇ㄥ灠缁犳牠鏌￠崶鈺佸壉闁搞倖娲熼弻宥堫檨闁告挻鑹鹃銉╁礋椤撴稑浜鹃梻鍫熺⊕閸熺偤鏌ｉ敐鍛埞闁宠棄顦甸獮姗€顢涘顐㈩棜濠电姷鏁搁崑娑㈡偋閸涱垰绶ゅ┑鐘冲搸閳ь兛绶氶獮瀣晜閼恒儲鐝柣搴″帨閸嬫捇鏌涢幇顔间壕闁哄倵鍋撻梻鍌欑閹诧繝宕濋弴銏犵疇閹兼番鍔岀粻?4 婵犵數鍋為崹鍫曞箹閳哄倻顩叉繝闈涱儏濮规煡鏌ｉ弬鍨倯闁哄拋鍓熼弻? y1 x2 y2闂?
_FRONT_ALIASES = {"front", "front:", "[front]", "f:", "f"}
_RIGHT_ALIASES = {"right", "overhead", "overhead:", "right:", "[right]", "r:", "r"}
_NUM_RE = re.compile(r"[-+]?[\d.]+(?:e[-+]?\d+)?", re.IGNORECASE)


def _parse_block_dict(text: str, block_name: str) -> CoordDict:
    out: CoordDict = {}
    for m in _BLOCK_RE.finditer(text):
        name = m.group("name").lower()
        if (block_name == "front" and name != "front") or (block_name == "right" and name != "overhead"):
            continue
        body = m.group("body")
        for mm in _PAIR_RE.finditer(body):
            gid = str(mm.group("id"))
            x1, y1, x2, y2 = (float(mm.group("x1")), float(mm.group("y1")),
                              float(mm.group("x2")), float(mm.group("y2")))
            out[gid] = [(x1, y1), (x2, y2)]
    return out


def _split_blocks_by_headers(lines: List[str]):
    blocks = {"front": [], "right": []}
    current = None
    for raw in lines:
        s = raw.strip()
        low = s.lower()
        if low in _FRONT_ALIASES:
            current = "front"; continue
        if low in _RIGHT_ALIASES:
            current = "right"; continue
        if not s or current is None:
            continue
        blocks[current].append(s)
    return blocks


def _parse_section_lines(lines: List[str]) -> CoordDict:
    """
    濠电姵顔栭崳顖滃緤閻ｅ本宕查悗锝庡墰閸楁岸鎮楅棃娑欏暈闁稿锕㈤幃姗€鎮欓弶鎴濆Б濡?4 婵犵數鍋為崹鍫曞箹閳哄倻顩叉繝闈涱儏濮规煡鏌ｉ弮鍥モ偓鈧柛瀣尭閳藉鈻庡Ο娲诲悈缂傚倷娴囨禍顒€鈻? y1 x2 y2
    闂傚倷鑳堕…鍫㈡崲鐎ｎ€㈠綊宕堕澶嬫櫓闂婎偄娲︾粙鎺楁倿缂佹ü绻嗛柕鍫濆€告禍楣冩偡?缂傚倸鍊风粈渚€鎯夋總绋跨？闁靛牆顦伴崑瀣煕濞戞﹫鍔熸い鈺咁棑缁辨挻鎷呮慨鎴簼缁旂喖宕奸妷锔惧幈闂佸湱鍎ら崹鍫曀夐姀锛勭?
    """
    out: CoordDict = {}
    idx = 0
    for ln in lines:
        nums = [float(x) for x in _NUM_RE.findall(ln)]
        if len(nums) < 4:
            continue
        x1, y1, x2, y2 = nums[:4]
        gid = f"{idx:05d}"
        out[gid] = [(x1, y1), (x2, y2)]
        idx += 1
    return out


def load_and_parse_data(filepath: str) -> Tuple[CoordDict, CoordDict]:
    """
    闂備礁鎼ˇ顐﹀疾濠婂牆钃熼柕濞垮剭?(front_dict, right_dict)闂傚倷鐒︾€笛呯矙閹烘梻鐭欓柟鐗堟緲缁犳煡鏌曡箛銉х？闁崇粯妫冮弻宥堫檨闁告挻鐩獮澶愬箻椤旂厧鑰垮┑掳鍊撻懗鍫曘€呴鐘电＝闁稿本鑹鹃埀顒佹倐楠炴牠顢曢敃鈧闂佺鎻粻鎴犵矆閸℃绠鹃柛鈩兠粭褏绱掗悩宕囧弨闁哄本鐩俊鐤槻濞寸姍鍥ㄧ厓?dict
    """
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # 1) 婵犵數鍋炲娆撳触鐎ｎ喗鏅梻浣告啞钃辩紒瀣尰缁傚秶绮欐惔鎾存杸婵犵數濮寸€氼厾鐟?block 闂佽崵鍠愮划蹇涘春閸ヮ剙鍨傞柛锔诲幗椤?
    front = _parse_block_dict(text, "front")
    right = _parse_block_dict(text, "right")

    # 2) 闂傚倷绀侀崥瀣儑瑜版帒纾块柟娈垮枟鐎氬鏌ｉ弮鍥仩闁活厽宀搁弻锝咁潩椤掑娈剁紓浣插亾濠㈣埖鍔栭崐鍫曠叓閸ャ劍鈷掔紒鐘冲哺閺岋綁鏁傜拠鑼桓闂佹悶鍔嶉崕鎶解€﹂妸鈺佺闁靛ě鈧崑鎾寸節濮橆厾鍘鹃梺鍛婄箓鐎氼剟鍩€椤掑倹鏆柛鈹惧亾濡炪倖甯婇懗鍓佺不閹剧粯鐓犻柛娑橈攻缁跺弶銇?
    if not front and not right:
        blocks = _split_blocks_by_headers(text.splitlines())
        front = _parse_section_lines(blocks.get("front", []))
        right = _parse_section_lines(blocks.get("right", []))

    return front, right

# ====== Processors (闂?processors.py) ======
# processors.py 闂傚倷鑳堕崑銊╁磿閺屻儱钃熼柨鐔哄Т閻?濠电姷鏁搁崑鐐哄箰閹间礁绠犻煫鍥ㄦ礈閻棝鏌涘畝鈧崑娑滅箽濠电偠鎻徊鍧椻€﹂崼銉﹀€甸柤濮愬€楃壕鍏笺亜閹扳晛鍔撮柛鐐舵缁辨帒螖閳ь剟鎯岄崒姘辨殾婵炲棙鎸婚崑鎰板级閸碍娅囬崡蹇撯攽閻戝洨鍒版繛鏉戝€垮畷鏉课旈崪浣规櫌?
from typing import Dict, List, Tuple, Optional
import math
import statistics

# Coord 闂?CoordDict 闂佽娴烽幊鎾诲箟闄囬妵鎰板礃椤帟鈧寧銇勮箛鎾跺婵☆偅锕㈤弻娑㈠Ψ椤栫偞顎嶅銈嗗姉閺咁偊鍩€椤掍緡鍟忛柛鐘冲浮瀹曟垿骞橀幇浣哄數闂佽偐顭堥悘姘辩礊閹达附鐓熼柨婵嗘搐娴滃墽绱?

# ----------------
# 闂傚倷鑳剁涵鍫曞疾閻愭祴鏋嶉柨婵嗩槶閳ь兛绶氬畷銊╊敇濠ф儳浜鹃柟鐑橆殔瀹告繃銇勯弮鍌濇婵?
# ----------------
def _len2(p1: Coord, p2: Coord) -> float:
    dx = float(p1[0]) - float(p2[0])
    dy = float(p1[1]) - float(p2[1])
    return dx*dx + dy*dy


def _segment_length(p1: Coord, p2: Coord) -> float:
    return math.hypot(float(p1[0]) - float(p2[0]), float(p1[1]) - float(p2[1]))


def _numeric_member_id(member_id: object) -> float:
    try:
        return int(base_id(member_id))
    except (TypeError, ValueError):
        return float("inf")


def _member_sort_key(member_id: object):
    num_id = _numeric_member_id(member_id)
    if num_id == float("inf"):
        return (1, str(member_id))
    return (0, num_id)


def _is_main_rod_candidate(member_id: object) -> bool:
    """Return whether the base drawing ID is eligible to be a class-1 rod."""
    return base_id(member_id).endswith(("01", "02", "03"))


def detect_main_rods_enhanced(coordinates_data: CoordDict, top_k: int = 2) -> List[str]:
    """
    Detect class-1/main rods among IDs ending in 01, 02, or 03.

    The eligible candidates are ranked by length first, then fall back to the
    smallest eligible IDs. Duplicate-instance suffixes are ignored only when
    evaluating the drawing ID suffix.
    """
    if len(coordinates_data) < top_k:
        return []

    rod_items = []
    all_ids = []
    for rod_id, endpoints in coordinates_data.items():
        if (
            not _is_main_rod_candidate(rod_id)
            or not isinstance(endpoints, (list, tuple))
            or len(endpoints) != 2
        ):
            continue
        rod_key = str(rod_id)
        num_id = _numeric_member_id(rod_key)
        all_ids.append((rod_key, num_id))
        p1, p2 = endpoints
        rod_items.append((rod_key, num_id, _segment_length(p1, p2)))

    if len(rod_items) < top_k:
        return []

    rod_items.sort(key=lambda item: item[2], reverse=True)
    candidates = [item[0] for item in rod_items[:top_k]]

    all_ids.sort(key=lambda item: (item[1], item[0]))
    min_two_ids = [item[0] for item in all_ids[:top_k]]
    if len(min_two_ids) < top_k:
        return []

    candidates_set = set(candidates)
    min_two_set = set(min_two_ids)
    min_one = min_two_ids[0]

    if candidates_set == min_two_set:
        result = min_two_ids
    elif min_one in candidates_set:
        result = candidates
    else:
        result = min_two_ids

    return sorted(result, key=_member_sort_key)

def clean_view(view: CoordDict, view_name: str, round_ndigits: Optional[int] = None) -> CoordDict:
    """
    - 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾寰婃禒瀣畳婵＄偑鍊栧褰掑磿閾忣偆顩锋い鏍仦閻?
    - 闂傚倷绀侀幉锟犳晪濡炪値鍘奸崲鏌ュ煝瀹ュ棙鍎熼柕濠忚吂閹稿懘姊洪崜鎻掍簼婵炲弶锚琚欓柟鐗堟緲缁犲綊寮堕崼鐔峰姢妞も晩鍓熼弻娑㈠Χ閸涙惌鈧鏌?
    - 闂傚倷绀侀幉锟犳偡椤栫偛鍨傞柛顐ｆ礀閻掑灚銇勯幒鍡椾壕濡炪伇鈧崑鎾剁磽娴ｇ缍侀柛妤€鍟块悾椋庢崉鐞涒剝顫嶅┑鐘诧工閸熺増绂嶅鍕閻庢稒顭囬惌瀣煛鐏炶濮傜€规洩缍佸畷鍗炩槈濞嗘劖鐝梻浣稿閸嬪懐鎹㈤崟顓犵煋濠靛倸鎲￠悡鏇㈡煙閹咃紞鐏忓繘鏌ｆ惔銊︽锭闁兼椿鍨跺﹢浣圭箾鏉堝墽绉柕鍡忓亾闂佸搫琚崐鏇㈡箒?None闂傚倷鐒︾€笛呯矙閹达附鍎楀〒姘ｅ亾濠碘剝鎸冲畷姗€顢旈崱娆戝姸闂佸搫顦遍崑鐐寸珶閸℃稒鍋℃繝闈涱儐閻撴洘绻涢崱妯哄濠⒀屽墴閺岋繝宕遍鐘敌滈梺?
    """
    out: CoordDict = {}
    for k, seg in view.items():
        if not isinstance(seg, (list, tuple)) or len(seg) != 2:
            continue
        p1 = (float(seg[0][0]), float(seg[0][1]))
        p2 = (float(seg[1][0]), float(seg[1][1]))
        if _len2(p1, p2) < 1e-12:
            continue
        if round_ndigits is not None:
            p1 = (round(p1[0], round_ndigits), round(p1[1], round_ndigits))
            p2 = (round(p2[0], round_ndigits), round(p2[1], round_ndigits))
        out[str(k)] = [p1, p2]
    return out


def remap_vertical_coordinates(
    view: CoordDict,
    source_height_span: Optional[Tuple[float, float]],
    target_height_span: Optional[Tuple[float, float]],
) -> CoordDict:
    """Map a view's CAD Y values onto the common reconstruction height span."""
    if source_height_span is None or target_height_span is None:
        return dict(view)

    source_low, source_high = source_height_span
    target_low, target_high = target_height_span
    source_height = float(source_high) - float(source_low)
    if abs(source_height) < 1e-9:
        return dict(view)

    out: CoordDict = {}
    for member_id, segment in view.items():
        points = []
        for x_value, y_value in segment:
            level = (float(y_value) - float(source_low)) / source_height
            # Small CAD drafting offsets may put an endpoint slightly beyond a
            # support end.  Keep it on the physical tower interval.
            level = min(1.0, max(0.0, level))
            target_y = float(target_low) + level * (float(target_high) - float(target_low))
            points.append((float(x_value), target_y))
        out[str(member_id)] = points
    return out

# ----------------
# 闂傚倷绀侀幉锛勬暜閹烘嚦娑樷槈濮橆厼浠忓銈嗗姧闂勫嫰寮查浣瑰弿婵妫楅獮妤呮煛閸℃鐭掗柡宀€鍠栭幃娆擃敆閳ь剟鎮橀敐鍥╃＜婵°倐鍋撻柤娲诲灥閻忔帒顪冮妶鍛閻庢凹鍙冨畷?
# ----------------
def find_supports(view: CoordDict) -> CoordDict:
    """
    闂傚倷娴囬妴鈧柛瀣尰閵囧嫰寮介妸褉濮囬柣搴㈣壘閵堟悂寮婚埄鍐ㄧ窞濠电姴鍠氬Λ娑樷攽閻愬弶顥撻柛銊ょ矙瀵偄顓奸崨顏呯€荤紓?婵犵數鍋為崹鍫曞箲娴ｇ硶鏋嶉柨婵嗩槸缁€鍕归悩宸剰闁哄绶氶弻鈩冨緞鎼淬垻銆婇梺鍦櫕閸犳牠寮婚弴銏犲耿闁哄洨濮存俊钘夆攽閻橆偄浜惧銈嗙墬缁牓鎮?01/02/03/04闂傚倷绶氬褍螞閺傛娓婚柟鐑樻⒒缁犳棃鏌″鍐ㄥ闁崇粯姊婚埀顒€绠嶉崕閬嶅箠韫囨稑纾块柟鐐灱濡插牓鏌熼悙顒€澧柛搴＄箻閺屾盯濡搁敂鍓х暭闂?
    婵犵妲呴崑鍡樻櫠濡ゅ啯宕查柛宀€鍊涢崶銊х瘈婵﹩鍓涙鍥⒑閻愯棄鍔氱€殿喖鐖奸、鏇熺鐎ｎ偆鍙嗗┑鐐村灦閻熝囥€傞崣澶岀闁绘挸瀛╁﹢鎵磼閸屾稑娴€规洖銈稿鎾偄閸濄儲袠闂備胶顢婃竟鍫ュ箵椤忓棛涓嶉柟瀵稿Ь婵娊鏌ょ喊鍗炲閻庢碍宀搁弻鏇熺珶椤栨艾顏柕鍫熺叀閺岋絾鎯旈敐鍡樻瘎濡炪們鍨归敃锕€鈻庨姀鐘斀閻庯綆鍋€閹峰綊姊洪崨濠勫缂佽鲸娲滅划鍫ュ礋椤栨稑浠梺閫涘嵆濞佳囨倶閿濆鐓冮悷娆忓閳洜鈧灚婢樼€氼垶藝瑜版帗鐓曢幖娣灪鐏忥妇鈧娲樺畝绋跨暦閸楃倣鏃€绻濋崘鈺傜彟闂傚倸鍊搁…顒勫礈閿曞倸纾诲┑鐘叉处閸嬬喐銇勯弮鍥撻柛搴ｅ枛閺屻劑寮崶褌姹楃紓浣插亾?
    闂傚倷绀佸﹢閬嶅磿閵堝洦鏆滈柍銉︽灱閺嬪秹骞栧ǎ顒€濡介柛搴㈩殕閵囧嫰骞樼捄鐩掞綁鏌?X 闂傚倷鐒﹂幃鍫曞礉瀹€鍕垫晞闁糕剝顨忛悞浠嬫倶閻愭彃鈷旀い鈺冨厴閹鎷呴崨濠呯缂備讲鍋撻柛鏇ㄥ亐閺€?503/504闂?
    """
    # 缂傚倸鍊烽悞锕傘€冭箛娑樼婵炴垶姘ㄩ崡姘舵煛婢跺鐒炬繛闂村嵆閺屾洘寰勫Ο铏逛化缂備焦鍔栭〃濠囧蓟閿熺姴鐒垫い鎺戝闁卞洭鏌￠崶鈺佹灆闁稿绶氬娲捶椤撗勬瘜闂佺顑嗛幑鍥蓟閿熺姴閱囨繝鍨姈绗戦梻渚€鈧偛鑻晶顖炴煟閻斿弶娅婇柛鈹惧亾濡炪倖宸婚崑鎾淬亜閿斿灝宓嗙€殿噮鍋婇、姘跺焵椤掑嫮宓佹慨妞诲亾妤犵偛顑夐、娑橆煥閸滀焦袩ID 闂備浇宕甸崰鎰版偡閵壯€鍋撳鐓庡⒋鐎规洖缍婇、娑㈡倷鐎涙ɑ鐝?
    support_ids = detect_main_rods_enhanced(view, top_k=2)
    out = {}
    for sid in support_ids:
        seg = view.get(sid)
        if not seg:
            continue
        out[str(sid)] = [(float(seg[0][0]), float(seg[0][1])),
                         (float(seg[1][0]), float(seg[1][1]))]
    return out

def find_horizontals(view: CoordDict, tol_y: float, exclude_support: bool = True) -> CoordDict:
    """Return near-horizontal members, optionally excluding detected non-horizontal supports."""
    support_ids = set()
    if exclude_support:
        for sid in detect_main_rods_enhanced(view, top_k=2):
            seg = view.get(sid)
            if not seg:
                continue
            (_, y1), (_, y2) = seg
            if abs(float(y1) - float(y2)) > float(tol_y):
                support_ids.add(str(sid))

    out: CoordDict = {}
    for k, seg in view.items():
        if str(k) in support_ids:
            continue
        (x1, y1), (x2, y2) = seg
        if abs(float(y1) - float(y2)) <= float(tol_y):
            out[str(k)] = [(float(x1), float(y1)), (float(x2), float(y2))]
    return out

# ----------------
# 闂傚倷娴囬妴鈧柛瀣尰閵囧嫰寮介妸褉濮囬柣搴㈣壘閵堟悂寮婚敐澶婄厸濞撴艾娲ゅ▓鍫曟⒑閹肩偛鈧洘顨ュ宀€浜介梻浣哄仺閸庤京澹曢銏犵劦?
# ----------------
class Line:
    __slots__ = ("k","b","vertical_x","ymin","ymax","id")
    def __init__(self, p1: Coord, p2: Coord, gid: str):
        x1,y1 = float(p1[0]), float(p1[1])
        x2,y2 = float(p2[0]), float(p2[1])
        self.id = gid
        self.ymin, self.ymax = (min(y1,y2), max(y1,y2))
        if abs(x1-x2) < 1e-12:
            self.k = None
            self.b = None
            self.vertical_x = x1
        else:
            self.k = (y2-y1)/(x2-x1)
            self.b = y1 - self.k*x1
            self.vertical_x = None

    def x_at(self, y: float) -> float:
        y = float(y)
        if self.vertical_x is not None:
            return float(self.vertical_x)
        # y = kx + b -> x = (y - b) / k
        if self.k is None or abs(self.k) < 1e-12:
            return float("nan")
        # 濠电姵顔栭崰妤冪紦閸ф纾归柡宓本瀵?self.b 婵犵數鍋為崹鍫曞箰閸濄儳鐭撶€规洖娲﹂～鏇灻归崗鍏肩稇闁?None闂傚倷鐒︾€笛呯矙閹达附鍋嬮柛鈩冾樅閸濆嫷鐓ラ柛鏇ㄥ幐閺?k 婵犵數鍋為崹鍫曞箰閸濄儳鐭撻梻鍫熷厷?None闂?
        return (y - float(self.b or 0.0)) / self.k

    def x_mid(self) -> float:
        ym = (self.ymin + self.ymax)/2.0
        return self.x_at(ym)

def build_support_models(view_support: CoordDict) -> List[Line]:
    models: List[Line] = []
    for gid, (p1,p2) in view_support.items():
        ln = Line(p1,p2,str(gid))
        models.append(ln)
    # 闂傚倷绀佸﹢閬嶁€﹂崼銉嬪洭顢曢敃鈧悞鍨亜閹哄秷鍏岄柣顓炴閺屻倝宕归銏紘缂?x闂傚倷鑳堕崑銊╁磿閼碱剚宕查柛鎰典簼閺嗘粓鏌熼幆褏鎽犻柛搴ｅ枛閻擃偊宕堕妷銉ュБ缂備讲鍋撳鑸靛姈閻撴盯鏌涘畝鈧崑鎰板磻閹炬枼妲堟慨姗堢稻閺呮瑩鏌ｆ惔锛勭Ш婵炶壈宕电划濠氬箣閿濆啩姹楅梺褰掓？缁€渚€鎯屽Δ鍛厸鐎广儱鍟俊鍧楁煃瑜滈崜锕傚礈閻旈鏆?
    models.sort(key=lambda L: L.x_mid())
    return models

def _extreme_x_at(models: List[Line], y: float) -> Tuple[float, float]:
    """
    闂傚倷绶氬鑽ゆ嫻閻旂厧绀夐幖杈剧到閸ㄦ繈鏌熷▓鍨灀闁?y 婵犵數濮伴崹鐓庘枖濞戞埃鍋撳顒佹喐婵″弶鍔曢埞鎴﹀窗閹跺﹤娲ょ壕鍏兼叏濮楀棗浜炴い鏂挎濮婃椽宕ㄦ繝鍕櫑闂佸憡蓱閻楁粓骞冮鈧弻鍡楊吋閸涱厼鏁ら梺鑽ゅ枑閻熴儳鈧凹鍙冨鍐差煥閸喓鍘甸梺缁樺姦閸撴瑩鎮橀妷锔轰簻闁哄洢鍔岄弸鐔兼煙椤栨稒顥堢€殿噮鍣ｅ畷鎺戔槈濮橆厽顔?x闂傚倷鐒︾€笛呯矙閹烘鍤岄柟瑙勫姂娴滃綊鏌涢妷顔煎缂佺姰鍎甸弻宥堫檨闁告挾鍠庨锝夊垂椤愩垻绐為柣搴秵閸嬪懎鈻撴导瀛樷拺闁革富鍘兼禍楣冩煕閵娧勫殌闁?x_at(y)闂傚倷鐒︾€笛呯矙閹达附鍎楀ù锝囧劋瀹曟煡鏌熸潏鍓х暠闁绘劕锕弻锝夊箛椤掑倹鎲兼繛瀵稿У閿曘垽骞冨Ο璺ㄧ杸闁规儳澧庨铏圭磽娴ｈ娈旈柣顓炲€搁锝夋偨缁嬭法鍔﹀銈嗗笂缁€浣烘?
    """
    xs = [m.x_at(y) for m in models]
    if not xs:
        return (0.0, 0.0)
    xs = [x for x in xs if math.isfinite(x)]
    if not xs:
        return (0.0, 0.0)
    return (min(xs), max(xs))

# ----------------
# 闂傚倷绀侀幖顐﹀船閹绘帩鍚嬮柛銉㈡櫇瀹曞爼姊绘担濮愨偓鈧柛瀣尰閵囧嫰寮介妸褉濮囬柣搴亢閸嬫劗妲愰幘瀛樺闁告繂瀚悗铏圭磽娴ｈ鈷愰柟绋垮暱閻ｅ嘲顫濈捄铏归獓闂佸湱顭堟鎼佸焵椤掍緡娈滈柡灞诲€栫缓鑺ュ緞婢跺宕虫俊鐐€ら崑鍕敄婢跺﹦鏆﹂柛顐ｆ礀缁€鍫㈡喐鎼淬劍鍋╅梺顒€绉甸悡鏇㈢叓閸パ屽剰濠碘€炽偢閺岋綁顢斿鍛潽缂備礁顑呴ˇ鎵崲濠靛洦濯撮柧蹇氼潐閸熸挳姊洪崫鍕垫Ц闁绘妫楅敃銏ゆ焼瀹ュ懐鏌у銈嗗姧闂勫嫰寮查鍕厱妞ゆ劧绲块惌宀€绱掗悩杈╃煓闁哄瞼鍠栧褰掑箛椤旂厧顬夐梻浣告惈椤戝倿寮查悩璇茬畺闁规儼妫勯悙濠囨煥閺傚灝鈷旈柟鎻掔秺濮婃椽宕ㄦ繝鍕櫗闂佹寧娲﹂崑鍡椢?
# ----------------
def correct_paired_horizontals(front_horizontal: CoordDict,
                               right_horizontal: CoordDict,
                               front_support_models: List[Line],
                               right_support_models: List[Line],
                               round_to_int: bool = False,
                               front_height_span: Optional[Tuple[float, float]] = None,
                               right_height_span: Optional[Tuple[float, float]] = None,
                               target_height_span: Optional[Tuple[float, float]] = None):
    """
    闂傚倷鑳堕…鍫㈡崲閹存繐鑰块柛锔诲幘缁€濠囨煙鐎涙ɑ鍎曢柣鏃傗拡閺佸倿鏌涘☉鍗炴灓缂佸濞婂娲偡閹殿喗鎲奸梺鍛婃⒐濞茬喖銆佸棰濇晪闁逞屽墮閻ｇ兘濡烽妷褎娈曢梺鍛婃处閸樺ジ鎷忕€ｎ喗鈷戦柟绋挎捣閳洟鏌よぐ鎺旂暫妞ゃ垺宀搁、娆戠驳鐎ｎ兘鍋撻弻銉︾厵闂侇叏绠戞晶顖炴煕婵犲洦娑ч柍钘夘樀楠炴﹢宕￠悙鈺佷壕婵°倕鎷嬮弫鍌涖亜閹哄棗浜惧銈嗘穿缂嶄礁鐣烽锕€绀嬫い鎰╁€曢獮鈧梻鍌欐祰琚欓柛瀣崌閺岋箑螣娓氼垱效闂傚鍓﹂崜鐔煎蓟閿熺姴鐒垫い鎺戝閺佸秵绻涢幋鐐垫噧妞ゅ繗顫夌换?
    """
    if not front_horizontal and not right_horizontal:
        return front_horizontal, right_horizontal

    def _to_list(hh: CoordDict):
        return [(k, (seg[0][1]+seg[1][1])/2.0) for k, seg in hh.items()]

    fl = _to_list(front_horizontal)
    rl = _to_list(right_horizontal)

    def _vertical_span(models: List[Line]):
        values = [value for model in models for value in (model.ymin, model.ymax)]
        if not values:
            return None
        low, high = min(values), max(values)
        return (low, high) if high - low >= 1e-9 else None

    def _relative_height(y: float, span):
        if span is None:
            return None
        low, high = span
        return (float(y) - low) / (high - low)

    matched_pairs = []
    # Support slopes are unified before this function runs.  Their resulting
    # common bounds cannot be used to compare CAD levels from two views with
    # different original vertical scales, otherwise corresponding members such
    # as 208/209 are rejected as being on different layers.
    front_span = front_height_span or _vertical_span(front_support_models)
    right_span = right_height_span or _vertical_span(right_support_models)
    if front_span and right_span:
        candidates = []
        for kf, yf in fl:
            front_level = _relative_height(yf, front_span)
            for kr, yr in rl:
                right_level = _relative_height(yr, right_span)
                candidates.append((abs(front_level - right_level), str(kf), yf, str(kr), yr))

        used_front = set()
        used_right = set()
        max_relative_height_gap = 0.04
        for gap, kf, yf, kr, yr in sorted(candidates):
            if gap > max_relative_height_gap:
                break
            if kf in used_front or kr in used_right:
                continue
            used_front.add(kf)
            used_right.add(kr)
            matched_pairs.append((kf, yf, kr, yr))

    for kf, yf, kr, yr in matched_pairs:
        if target_height_span and front_span and right_span:
            front_level = _relative_height(yf, front_span)
            right_level = _relative_height(yr, right_span)
            level = min(1.0, max(0.0, (front_level + right_level) / 2.0))
            y = target_height_span[0] + level * (target_height_span[1] - target_height_span[0])
        else:
            y = (yf + yr)/2.0

        Lf, Rf = _extreme_x_at(front_support_models, y)
        Lr, Rr = _extreme_x_at(right_support_models, y)

        if round_to_int:
            y, Lf, Rf, Lr, Rr = round(y), round(Lf), round(Rf), round(Lr), round(Rr)

        front_horizontal[str(kf)] = [(Lf, y), (Rf, y)]
        right_horizontal[str(kr)] = [(Lr, y), (Rr, y)]

    # 2) 闂傚倷绀侀幉锟犲箰閹绢喖鐤炬繛鍡樺灩缁€濠囨煙鏉堝墽鐣遍悗姘槹閵囧嫯绠涢幘璺侯暫闁汇埄鍨辨繛濠囧箖濡ゅ懏鍋ㄦ繛鍫熷閺侇垶姊洪柅鐐茶嫰婢ь噣鏌熼崘鏌ュ弰妤犵偛鍟村畷鍫曨敆娴ｅ憡鐤佹俊鐐€曠换鎰板箠鎼淬劍鍎婂┑鐘崇閻撴盯鏌涢顐簻濠⒀冨级閵囧嫰顢曢姀鈺佸壎閻庤娲栭悥濂稿箖濞嗘搩鏁嗗ù锝堫潐椤斿洭姊绘担鍛婅础闁稿鎹囧畷褰掓嚋閸偄寮块梺鎼炲労娴滄绂?
    def _project_rest(hh: CoordDict, models: List[Line], used_keys: set):
        for k, seg in list(hh.items()):
            if k in used_keys:
                continue
            y = (seg[0][1]+seg[1][1])/2.0
            L, R = _extreme_x_at(models, y)
            if round_to_int:
                y, L, R = round(y), round(L), round(R)
            hh[str(k)] = [(L, y), (R, y)]
    _project_rest(front_horizontal, front_support_models, {kf for kf, _, _, _ in matched_pairs})
    _project_rest(right_horizontal, right_support_models, {kr for _, _, kr, _ in matched_pairs})

    return front_horizontal, right_horizontal

# ================================
# 闂傚倷绀侀幖顐﹀磹閻熼偊鐔嗘慨妞诲亾鐠侯垶鏌涢幇闈涙灍闁哄拋鍓氶幈銊ノ熼幐搴ｅ涧缂佺虎鍘奸悥濂稿箖瀹勬壋鏋庨煫鍥ㄦ濡偛鈹戦悙鑼憼闁挎洏鍨介悰顔锯偓锝庡枛缁犳稒銇勯幒鎴Ц婵炲牆鎽滅槐鎾诲磼濞嗘帒鍘￠梺鍝ュТ缁夊墎鍒掗埡鍛妞ゆ棁鍋愰崫妤€顪冮妶鍡欏缂佸甯為埀顒佽壘閵堟悂寮婚敓鐘茬＜婵炴垶姘ㄩ悡鍌炴倵?+ 婵犵绱曢崑鎴﹀磹濞戙垹鏄ラ柡宥庡幗閹酣姊绘担鍛婃儓妞わ富鍨拌灋婵炴垯鍨洪崑銈夋煙鏉堥箖妾柍?+ 闂傚倷娴囬妴鈧柛瀣尰閵囧嫰寮介妸褉濮囬柣搴㈣壘閵堟悂寮婚悢鍝勬瀳婵☆垳绮悵鏃堟⒑?+ 婵犵數鍋涢顓熸叏閹绢喖绠犵€广儱娲ㄧ粈濠囨煙鐎涙ɑ鍎曢柣鏃傗拡閺佸倿鏌涘☉鍗炴灓缂佸娅曠换娑氣偓娑櫭▓鐘绘煕婵犲喚娈滅€?
# ================================

def match_support_slopes(front_support: CoordDict,
                                     right_support: CoordDict,
                                     strategy: str = "mean",
                                     unify_bounds: bool = True,
                                     round_to_int: bool = False,
                                     y_round_to_int: bool = False) -> Tuple[CoordDict, CoordDict]:
    """
    闂備浇宕垫慨鍨娴犲绀夐煫鍥ㄥ喕缂嶆牠鎮楅敐搴℃灈闁绘劕锕鍝勨枎閹呬粴闂佺顑嗛幐鎼佲€﹂妸鈺佺妞ゆ劑鍊撳ù鐑芥⒑鐠囨煡鍙勬繛浣冲洤鍌ㄦ繝濠傜墕閻掑灚銇勯幒宥堝厡缂佺姵顭囩槐鎺楊敊閹冨缂備礁顑呴ˇ鐢稿春閳ь剚銇勯幒鎴濐仼缂備讲鏅滈妵鍕冀閵娧€濮囬柣搴㈣壘閵堟悂寮婚敓鐘茬＜婵炴垶姘ㄩ悡鍌炴倵閸︻収鐒鹃柕鍫熸倐瀵偄顓奸崪浣瑰兊濡炪倖鍔х槐鏇㈡瀹ュ鍊电憸鐗堝笚娴溿倗绱掗悩鍐茬伇闁靛洦鍔欓獮鏍ㄦ媴缁嬪灝娈ゅ┑鐐舵彧缁茶法娑甸崼鏇炵；闁规崘顕х粈鍌炴煕韫囨挸鎮戞繛鍫滃嵆濮婃椽宕烽鐐板闂佹悶鍔屽鈥崇暦閵忋倕围闁搞儻绲芥禍楣冩煟閵忕姷浠涙い蹇曞枔缁辨帗娼忛妸褎鍣у銈嗘煥缁绘﹢寮崒鐐村仭闁绘鐗婇悵顐︽煟鎼达紕绉烘繛鑹板吹閹峰綊鎮㈤悡搴ｅ姦濡炪倖鍨煎▔鏇⑺囬敂鐐枑闁绘鐗婇崐鎰版煕閳轰焦顥㈢€殿噮鍓熷畷褰掝敊缂併垺袦闂傚倷鐒︾€笛呯矙閹次层劑鍩€椤掑倻纾?
    闂備浇顕х换鎰崲閹邦儵娑樷攽鐎ｎ亜鍋嶉梺闈涚墕濞茬娀宕戦幘缁樺仺闁割煈鍋勫▓宀勬⒑鐠団€虫灍妞ゃ劌锕獮鍡涘礃椤旇偐顦板銈嗗笂閼宠埖绂掗幒妤佲拺?k 婵犵數鍋為崹鍫曞箰閹绢喖纾婚柟鍓х帛閻撶娀鏌ｉ妶搴＄仭鐟滄妸鍛＜閺夊牄鍔庨幊鍕亜椤忎礁浜炬繝纰樻閸ㄩ亶顢栧▎鎾宠Е闁搞儺鍓氶悡鏇熺箾閸℃ê濮夊褜浜濈换娑㈡偂鎼淬劌寮伴悗瑙勬礃閸旀鈽夐崹顐Ч閹艰揪缍嗗Σ鎾⒒娴ｇ懓顕滅紒瀣灴閹崇喖顢涢悙鏉戞闂佺粯姊婚崢褏绮婚灏栨斀闁绘ɑ褰冮鏉懨归悡搴♀偓鍧楀蓟閿濆绠涙い鎺嶆祰绾偓缂傚倷绶￠崰姘跺磿閵堝洨鐭欏鑸靛姇閻掑灚銇勯幒鎴濐仼缂佲偓閸℃稒鐓欑€瑰嫮澧楀﹢鎵棯椤撶偟鍩ｉ柟顔煎槻閳诲氦绠涢弮鎴烆棧婵犵數鍋涢悺銊╂晝閵忕姷鏆︽俊銈呮噹鎯熼梺闈涳紡閸曨剙顏?ymin/ymax闂?
    """
    if not front_support or not right_support:
        return front_support, right_support

    ys = [p[1] for seg in front_support.values() for p in seg] + \
         [p[1] for seg in right_support.values() for p in seg]
    if not ys:
        return front_support, right_support

    gmin, gmax = (min(ys), max(ys))

    F_models = build_support_models(front_support)
    R_models = build_support_models(right_support)
    if len(F_models) == 0 or len(R_models) == 0:
        return front_support, right_support

    def _extremes(models):
        if len(models) == 1:
            return models[0], models[0]
        return models[0], models[-1]

    F_left, F_right = _extremes(F_models)
    R_left, R_right = _extremes(R_models)

    def _target_k(k1, k2):
        if strategy == "front": return k1
        if strategy == "right": return k2
        # 婵犳鍠楃敮妤冪矙閹烘せ鈧箓宕奸妷顔芥櫍婵犵數濮甸懝楣冩煥閵堝鐓曢柕澶嬪灍閸嬫捇鏌涚€ｎ偅灏垫繛鎴濈仛椤︾増鎯旈檱閳ь剙娼″娲箹閻愭彃顬堥梺绋匡龚椤曆呭弲闁荤姵浜介崝搴∥涢鐐寸厱闁哄秶鏁哥壕璺ㄧ磼閳ь剟宕?None闂傚倷鐒︾€笛呯矙閹次诲洭顢欓崜褏鐣堕柣蹇曞仧閸嬫挻绂嶉妶澶嬬厵閻庣數顭堟禒锕傛倵閸偆鐭嬫い銊ｅ劦閹瑩鎳犻濠勭濠电姰鍨奸～澶屾暜閹烘鐓濋柟鎯ь嚟缁♀偓闂佺琚崐鏍吀闂?
        if k1 is None and k2 is None:
            return None
        if k1 is None:
            return k2
        if k2 is None:
            return k1
        return (k1 + k2) / 2.0

    kL = _target_k(F_left.k,  R_left.k)
    kR = _target_k(F_right.k, R_right.k)

    def _rebuild(line: Line, k_new):
        y_anchor = (gmin + gmax) / 2.0
        x_anchor = line.x_at(y_anchor)
        if k_new is None:
            # 闂傚倷鐒﹂幃鍫曞礉瀹€鍕９閻犲洩顥嗛搹瑙勫磯闁靛ě鍕剁础闂備礁鎲￠悧顓犳閺囩姷鐜绘俊銈傚亾閼挎劙鏌涢妷锝呭缂佺姵鐗犻幃妤呭垂椤愶絺鎷荤紓渚囧枓閺呯姴顕ｆ禒瀣垫晝闁挎繂娲ら崵鍗炩攽閻愯埖褰х紒鑼舵铻炴繝闈涱儏閻掑灚銇勯幒宥嗩樂濞存嚎鍨荤槐鎺旀嫚閹绘帗娈婚梺鍝勮閸斿矂锝炲┑瀣闁绘劖婢樼€?x
            x_top = x_anchor
            x_bot = x_anchor
        else:
            kk = float(k_new)
            if abs(kk) < 1e-12:
                kk = 1e-12 if kk >= 0 else -1e-12
            x_top = x_anchor + (gmin - y_anchor) / kk
            x_bot = x_anchor + (gmax - y_anchor) / kk
        y1, y2 = (gmin if unify_bounds else line.ymin, gmax if unify_bounds else line.ymax)
        if y_round_to_int:
            y1, y2 = round(y1), round(y2)
        if round_to_int:
            x_top, x_bot = round(x_top), round(x_bot)
        return [(x_top, y1), (x_bot, y2)]

    front_support = dict(front_support)
    right_support = dict(right_support)
    front_support[F_left.id]  = _rebuild(F_left,  kL)
    right_support[R_left.id]  = _rebuild(R_left,  kL)
    front_support[F_right.id] = _rebuild(F_right, kR)
    right_support[R_right.id] = _rebuild(R_right, kR)
    return front_support, right_support


def _highest_horizontal_key(view_h: CoordDict) -> Optional[str]:
    if not view_h: return None
    items = sorted(view_h.items(), key=lambda kv: (kv[1][0][1]+kv[1][1][1])/2.0)  # y闂備胶鍎甸崜婵堟暜閹烘鏅濋柕鍫濐槹閸庡秵銇勯幒鎴濃偓褰掑箚閵夈儮鏀介柣妯哄级瀹告繄鎲?
    return items[0][0] if items else None

def _xset_at(models: List[Line], y: float) -> List[float]:
    xs = [m.x_at(y) for m in models]
    xs = [x for x in xs if math.isfinite(x)]
    xs.sort()
    return xs

def _best_pair_near_width(Xs: List[float], target: float) -> Optional[Tuple[float, float]]:
    if len(Xs) < 2: return None
    C = (min(Xs) + max(Xs)) / 2.0
    best = None
    for i in range(len(Xs)-1):
        for j in range(i+1, len(Xs)):
            L, R = Xs[i], Xs[j]
            w = R - L
            err = abs(w - target)
            ctr = (L + R) / 2.0
            cen = abs(ctr - C)
            cand = (err, cen, L, R)
            if best is None or cand < best:
                best = cand
    if best is None:
        return 0.0, 0.0
    _, _, L, R = best
    return L, R

def plan_top_span(
    front_support_models: List[Line], right_support_models: List[Line],
    front_horizontal: CoordDict, right_horizontal: CoordDict,
    length_mode: str = "min",            # "min" | "mean" | "front" | "right"
    pair_mode: str = "extreme"           # 闂傚倷绀侀幖顐﹀磹閻熼偊鐔嗘慨妞诲亾鐠侯垶鏌涢幇闈涙灍闁?extreme"=闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鐐墯閻斿棝鏌ら崫銉︽毄濠⑿板洦鐓涢柛娑卞幘閸╋絾顨ラ悙宸剶妤犵偛娲、妤佸緞婵犲喚鍟呴梻?best"=闂傚倷绀侀幉锟犫€﹂崶顒€绐楅幖娣妼閸屻劍绻涢幋娆忕仼閻庢艾顦甸弻宥堫檨闁告挾鍠栭悰顕€骞掑Δ鈧敮闂侀潧臎閸滀礁鏁堕梻鍌欒兌閸庣敻寮查埡鍛獥婵°倕鎳忛崑澶愭煥濠靛棙绀岄柛瀣尵濞戠敻宕ㄩ鍛棄闂?
):
    """
    闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晛鈹戦悩瀹犲闁诲繗娅曠换婵囩節閸屾稑娅ч梺鍦帶閵堢顫忔繝姘劦妞ゆ帒瀚柨銈嗕繆閻愯尙姣為柛瀣尰缁绘繈宕戦悾灞芥灈妞ゃ垺妫冨畷銊╊敊閸擃灝锟犳⒒娴ｅ搫浠洪柛搴ゅ皺閹广垽宕熼鐔哥亖闂佺鎻粻鎴犵矆閸岀偞鐓曟俊銈呭暙娴狅箓鏌涙繝鍌氳埞妞ゎ亜鍟存俊鍫曞川椤栨氨鍘介梻?y_top 婵犵數鍋涢顓熸叏娴兼潙纾块柛妤冨剱閸ゆ洟姊洪崹顕呭剳闁崇粯妫冮弻鏇㈠醇濠靛牆鈷堝┑鐐插悑鐢繝寮诲☉銏犖ㄩ柕澶堝劗閹稿啫顪冮妶鍛闁告挾鍠栭獮?L/R闂?
    - 闂?pair_mode="extreme"闂傚倷鐒︾€笛呯矙閹烘埈娼╅柕濞垮剭濞差亜閿ゆ俊銈傚亾缂佺姵濞婇弻鏇熷緞閸繂濮庣紓浣瑰絻濞硷繝寮诲澶娢ㄩ柨鏂垮⒔閻撲礁鈹戦悙瀛樺磩婵炲鐩、?闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鍓х帛閻撴洘绻涢崱妯哄闁诲繘浜堕弻宥堫檨闁告挻姘ㄩ幑銏ゅ焵椤掑嫭鍋犳慨妯绘构閹插墽鈧鍠氶弲顐﹀箟閹绢喖绀嬫い鎺嶇劍椤斿洭姊绘担鍛婅础闁稿鎹囧畷鐑樼節閸曨剦娼熷┑鐘绘涧椤戝懘骞?y_top 婵犵數濮伴崹鐓庘枖濞戞埃鍋撳闂撮偗鐎规洦鍓熼、妤呭礋椤愩値妲梻渚€娼ч¨鈧┑鈥虫搐閿曘垽寮堕幊銊ф嚀閳瑰啴宕归鐟颁壕闁哄洨濮甸浠嬫⒑椤掆偓缁夊绮?(Lf,Rf)/(Lr,Rr)闂?
    - 闂?pair_mode="best"闂傚倷鐒︾€笛呯矙閹烘鍎楁い鏃傚亾瀹曞弶鎱ㄥΟ鍨厫闁稿鏅滅换娑㈠幢濡ゅ啰顔囬梺鍝勫€戦崶銊у幈闂婎偄娲﹂幐鐐櫠閺囩喓绡€闁逞屽墴椤㈡棃宕煎┑鍫悑闂備線鈧偛鑻晶瀵糕偓娈垮枛閻忔艾顕ラ崟顓涘亾閿濆骸浜濇繛鍫滃嵆濮婃椽宕烽鐐板闂佹悶鍔屽鈥崇暦閾忣偒妲归幖瀛樏禍楣冩煟閵忋垺鏆╅悽顖涚☉椤法鎲撮崟鎯扳偓璺ㄢ偓娈垮枤閺佸宕洪埀顒併亜閹烘垵顏╃紒鐘冲▕閺屾洘寰勯崼婵嗩瀷缂備胶濯崳锝夊蓟閿濆鐓涘┑鐘插€归悘宥夋⒑缂佹澹勭紒鎻掓健閸┾偓妞ゆ帒鍋嗛弨鐗堜繆椤愩垹顏柍褜鍓濋～澶嬬箾婵犲洤绠氶柛鎰靛枛缁€瀣亜韫囨挻锛嶅ù鐓庢喘閺岋絾鎯旈妸锔介敪缂備胶濮寸粔褰掑春閳?
    """
    if not front_support_models or not right_support_models:
        return None

    # 1) 闂傚倷鑳堕…鍫㈡崲閹扮増鍋嬪┑鐘插閸嬫捇宕归銈囩厜闂佹悶鍔嶉崕鎶解€﹂妸鈺佺妞ゆ垼娉曠敮娑樷攽鎺抽崐鏇㈠磹绾懏鎳岄梻浣瑰劤濡繈寮婚埄鍐ㄧ窞濠电姴鍠氬Λ蹇涙⒑闁偛鑻晶顖滅磼鐠囨彃鏆ｉ柟顖氭处鐎靛ジ寮堕幋鐙€妲梻浣告啞椤ㄥ牓宕戦悙鍝勭９闁告鍎愬〒濠氭煏閸繃鍣介柛鈺嬬秮閺岋絽鈹戦幇顒佺彎闂佽桨绀佺粔鐟扮暦閻撳寒鐓ラ柛娑卞灙濡插牓姊绘担铏瑰笡缂侇喖瀛╅弲璺何旈埀顒勬晝閵忥紕鐟归柍褜鍓熼獮?y_top 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晝绱撴担璇＄劷闁崇懓绉电换婵嬫濞戞瑦鎮欓梺浼欏瘜閸犳牠鍩ユ径鎰鐎规洖娉﹂姀銏″枑闁哄顑欏Ο鈧梺?
    def _highest_y(view_h: CoordDict):
        if not view_h: return None
        k = _highest_horizontal_key(view_h)
        if k is None: return None
        seg = view_h[k]
        return (seg[0][1] + seg[1][1]) / 2.0

    y_candidates = []
    yf = _highest_y(front_horizontal)
    yr = _highest_y(right_horizontal)
    if yf is not None: y_candidates.append(yf)
    if yr is not None: y_candidates.append(yr)
    if not y_candidates:
        return None
    y_top = sum(y_candidates) / len(y_candidates)

    # 闂備浇顕х换鎰崲閹邦喗宕查柟閭﹀幖椤曢亶鏌熼悧鍫熺凡缂佲偓閸岀偞鐓曢柟瀛樼懃閳ь剚顨堢划锝呂旈崨顔惧幈濠电偛妫欓崝妤佹櫠閵堝鐓冪憸婊堝礈濮樺崬鍨濈€广儱鎳岄埀顒佸笧閹瑰嫭绗熼姘珚?闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鍓х帛閻撴洘绻涢崱妯哄闁诲繘浜堕弻宥堫檨闁告挻姘ㄩ幑銏ゅ焵椤掑嫭鍋犳慨妯绘构閹插墽鈧鍠氶弲顐﹀箟閹绢喖绀嬫い鎺嶇劍椤斿洭姊绘担鍛婅础闁稿鎹囧畷鐑樼節閸曨剦娼熷┑鈩冨劤瀹撴攰ld_support_models 闂佽楠稿﹢閬嶁€﹂崼婵愬殨闁告挷璁查崑鎾诲垂椤愩倗鐓€濡炪値鍋呯换鍫濐嚕閸洖绠ｉ柨鏃囨閻ㄥ搫鈹戦悙鑸靛涧缂佽尙鏅划鏃堝醇閺囩喎浠鹃梺绯曞墲缁嬫垹绮婚幎鑺ョ厵闁绘垶锚閻忊晝鐥弶璺ㄐч柡?
    def _extremes(models):
        if len(models) == 1:  # 闂傚倷绀侀幉锟犳偡椤栨稓顩叉繝闈涙４閼板灝霉閿濆懏璐￠柍缁樻閺屽秷顧侀柛鎾跺枎椤曪絾绂掔€ｎ偆鍔靛┑鐐村灦濮樸劌危韫囨稒鈷戦柣鎾抽閺嗛亶鏌嶈閸撴盯宕伴幘鍓佷笉闁哄被鍎查悡鏇㈡煏婢诡垰鍟╃划鍫曟⒑鐠団€虫灍闁规瓕宕电划娆愬緞閹邦剛鍔﹀銈嗗笒鐎氼剟宕橀埀顒勬⒑鐠嬪骸鍟幉鍝ョ磼閳ь剚寰勯幇顓涙嫼濡炪倖宸婚崑鎾绘煟韫囨梻绠炵€规洏鍨芥俊鍫曞川椤栨稒顔?
            return models[0], models[0]
        return models[0], models[-1]

    # 闂備浇顕х换鎰崲閹邦喗宕查柟閭﹀幖椤曢亶鏌熼悧鍫熺凡缂佲偓閸岀偞鐓曢柟瀛樼懃閳ь剚顨堢划锝呂旈崨顔尖偓鐢告煟閻旂厧浜版俊鍙夋倐閺屾稑鈻庤箛鏇狀啋閻庤娲滈崗妯侯嚕閸洖绠伴幖娣€曢幆?y_top 婵犵數濮伴崹鐓庘枖濞戞埃鍋撳鐓庡⒉闁靛洦鍔欏畷鍫曞Ω瑜滃ú鎼佹⒑闂堟稓澧曟繛灞傚€栫粋?x闂傚倷鐒︾€笛呯矙閹达附鍋嬮柟鐗堟緲閻掑灚銇勯幒鍡椾壕闂佸摜鍠庨崯鍧椻€栨繝鍥ㄥ殥闁靛牆娲ゅ畷銉╂⒑閸濆嫮鈻夐柛瀣噽閻ヮ亪顢涘鍛紲?闂備礁鎼ˇ顐﹀疾濠婂牆鍨傞柛顐ｆ礀缁犳澘顭块懜闈涘鐎规挷鑳堕埀顒冾潐濞叉牕煤閵堝應鏋旈柣妯肩帛閻?
    def _x_at(line_model: Line, y: float) -> float:
        if getattr(line_model, "vertical_x", None) is not None:
            return float(line_model.vertical_x or 0.0)  # type: ignore
        k = getattr(line_model, "k", None)
        b = getattr(line_model, "b", None)
        if k is None or abs(k) < 1e-12:
            # 闂傚倷绀侀幖顐︻敄閸曨垱鍤勯柛顐ｆ处閺佸倹銇勯幒鎴濐仾闁绘帒顭烽弻宥堫檨闁告挾鍠庨悾鐑芥偐鐠囨彃鍞ㄩ梺姹囧灮閺佹悂鎮伴妷鈺傜厸濠㈣泛妫欏▍鍡涙煕閵娿儳鍩ｆ鐐村姈瀵板嫰骞囬鑲┿偊闂備焦鍎冲ù姘跺磻閸涙潙姹叉繝濠傜墛閻撴瑩鏌ｉ幇闈涘闁绘挴鍋撶紓鍌欑窔娴滆埖绂嶇捄铏规殾闁挎繂顦崘鈧銈嗗笒椤︻垰鈻撳▎鎾粹拺閻炴稈鈧厖澹曟俊鐐€栭悧妤冪矙閹烘柡鍋撳鍐蹭汗闁瑰弶鎮傞幃褔宕奸悢椋庮暡濠电姭鎷冮崨顓涙瀰闂佹悶鍔嶉崕鎶解€﹂妸鈺佺劦妞ゆ帒瀚崵鍫ユ煙鏉堝墽鎮奸柣銈傚亾?x闂傚倷鑳堕崑銊╁磿閼碱剚宕查柍褜鍓涚槐鎾愁吋閸℃ǚ鎷圭紓浣割儏椤﹂潧鐣烽锕€绀嬫い鎰╁灮椤斿姊?
            return (getattr(line_model, "xmin", 0.0) + getattr(line_model, "xmax", 0.0)) / 2.0
        return (y - float(b or 0.0)) / k  # type: ignore

    # 2) 闂傚倷鑳堕崕鐢稿疾濞戙垺鍋ら柕濞у嫭娈伴柣搴㈢⊕椤洭銆呴悜鑺ョ叆婵犻潧妫欓崳鍦偓娈垮枟婵炲﹪寮诲☉銏犵闁圭偓鍓氬Λ搴ㄦ⒑闁偛鑻晶顖滅磼椤旇偐孝闁靛棙甯￠幊婊堟濞戞氨鐛梻浣告惈缁嬪嫰姊介崟顐熸瀺闁绘绮悡娑㈡煃瑜滈崜鐔笺€佸☉妯锋婵炲棗娴氭导鏍⒒娴ｅ搫浠洪柛搴ゅ皺閹广垽宕掑鎹愨偓?y_top 闂傚倷鐒﹂惇褰掑礉瀹€鈧埀顒佸嚬娴滄粓锝炲┑瀣櫇闁稿本绋戦埀顒傚厴閺岋綀顦查柟鑺ョ矌缁牊寰勭仦绋夸壕闁汇垽娼ч。鍏笺亜閵娿儲鍤囩€规洖鎼悾婵嬪礋椤愩垹浜堕梻浣虹帛閺屻劑銆冩惔鈽嗙劷婵°倕鍟扮壕濂告煛閸愨晛鐏ラ柣蹇ョ秮閺屾稓鈧絽澧庨幃濂告煃?
    if pair_mode == "extreme":
        F_left, F_right = _extremes(front_support_models)
        R_left, R_right = _extremes(right_support_models)
        Lf0, Rf0 = _x_at(F_left, y_top), _x_at(F_right, y_top)
        Lr0, Rr0 = _x_at(R_left, y_top), _x_at(R_right, y_top)
        if Lf0 > Rf0: Lf0, Rf0 = Rf0, Lf0
        if Lr0 > Rr0: Lr0, Rr0 = Rr0, Lr0
        Wf0, Wr0 = (Rf0 - Lf0), (Rr0 - Lr0)

        # 3) 婵犵數鍋涢顓熸叏鐎靛摜鐭撻柣鐔诲焽閳ь剚甯″畷濂稿即閻愬吀绱滄繝鐢靛Т閿曘倝骞婇幇鏉跨濠靛倸鎲￠埛鎺楁煃瑜滈崜姘跺箚閺冨牆绠绘い鏍ㄧ煯婢规洖鈹戦悩缁樻锭闁哥喓濞€瀹曟垿骞樼拠鍙夘棟闁荤偞绋堥埀顒€鍘栨竟鏇㈡⒑閸濆嫬鏆欓柛濠傜秺瀵?length_mode 闂傚倷绀侀幉锟犲礉閺囥垹鐤柛褎顨嗛崑鈺佄旈敐鍛殲闁稿骸瀛╅妵鍕籍閸屾稒鐝梺鎼炲妼閵堟悂骞冨Δ鍐╁厹闁告侗鍣Λ鍕煟?Wt闂傚倷鐒︾€笛呯矙閹达附鍤愭い鏍仦閸ゆ劙鏌ｉ弬鎸庢喐妞も晝鍏橀弻鏇熷緞閸繂濮曢梺绋匡攻椤ㄥ﹪寮婚妶鍡欓檮濠㈣泛顦遍懗娲⒑閻撳海浠涢柛銊ㄥ亹缁鈽夐姀鐘殿槰閻熸粍鍨圭划鍫⑩偓锝庡枛缁狙囨煟閹邦剛鎽犵紓宥嗗灥闇夐柣妯虹－閵嗘帡鏌嶈閸撶喎顭囪閿曘垺娼忛鐔峰緮闂傚倷娴囬妴鈧柛瀣崌閺屾盯骞橀懠璺哄帯缂?闂傚倷绀佸﹢閬嶃€傛禒瀣柧婵炴垶纰嶉～?
        if length_mode == "front":
            Wt = Wf0
        elif length_mode == "right":
            Wt = Wr0
        elif length_mode == "mean":
            Wt = (Wf0 + Wr0) / 2.0
        else:  # "min"闂傚倷鐒︾€笛呯矙閹烘鍎楁い鏃傚亾瀹曞弶鎱ㄥΟ璇差暢闁稿鎹囬幃鐑藉箥椤旂⒈鏆柣鐔哥矋濠㈡ê煤閿曗偓椤洩绠涘☉妯碱槰闂侀潧臎閸曨厽顫滈梻?
            Wt = min(Wf0, Wr0)

        Cf, Cr = (Lf0 + Rf0) / 2.0, (Lr0 + Rr0) / 2.0
        Lf, Rf = Cf - Wt / 2.0, Cf + Wt / 2.0
        Lr, Rr = Cr - Wt / 2.0, Cr + Wt / 2.0

    else:
        # 婵犵數鍎戠徊钘壝洪敂鐐床闁告洦鍨板Ч鏌ユ煃瑜滈崜娆撴箒闂佹寧绻傚ú銈呯摥闂佹眹鍩勯崹濂稿磻婵犲偆鍤曢柛顐ｆ礀鍞悷婊冮叄閹箖鏌嗗鍡欏帗闂侀潧顧€婵″洭鎯屾繝鍐瘈闁逞屽墴椤㈡棃宕煎┑鍫悑闂備線鈧偛鑻晶瀵糕偓娈垮枛閻忔艾顕ラ崟顓涘亾閿濆骸浜濇繛鍫滃嵆濮婃椽宕烽鐐板闂佹悶鍔岄悘婵嬪煝閺冨牊鏅濋柛灞句亢琚濋梻浣稿閸嬪懐鍒掕箛娑樺偍妞ゆ帒瀚悡娆撴⒒閸喓鈽夌紓宥嗙墱缁辨帡寮▎鎯ф闂侀€炲苯鍘哥紒鎻掝煼閿濈偞寰勬繛搴撳亾閹烘閱囬柡鍥╁仧椤斿﹪姊洪棃娑辨Ф闁告柨娴风划濠氼敋閳ь剟寮婚敐澶婄厸濠电姴鍊归悘宥夋⒑缂佹澹勭紒鎻掓健閸┾偓妞ゆ帒鍋嗛弨鐗堜繆椤愩垹顏柍褜鍓濋～澶嬬箾婵犲洤鍨傞柟顖嗏偓閺€浠嬫煕椤愩倕鏋旈柡鍡欏█濮婄粯绗熼崶褌绨煎┑鈥冲级鐢偛鈻庨姀銈庢晝闁挎棁濮ゅ▍鏍⒑閸撴彃浜濈紒璇插€垮顒冾槻闂囧鏌ｅ▎蹇斿櫧闁诡喖銈搁弻锝夊冀閵娧呯厜閻庢鍠撻崝鎴︾嵁閹达箑绠涙い鏃傝檸閸熷洭姊婚崒娆戝妽鐟滄澘鍟撮幊鐔碱敍濮樿鲸娈奸梺绯曞墲缁嬫垿鎯屽Δ浣典簻闁哄秲鍎遍埀顒侇殘缁?
        Xf = _xset_at(front_support_models, y_top)
        Xr = _xset_at(right_support_models, y_top)
        if len(Xf) < 2 or len(Xr) < 2:
            Lf, Rf = (min(Xf), max(Xf)) if len(Xf) >= 2 else (None, None)
            Lr, Rr = (min(Xr), max(Xr)) if len(Xr) >= 2 else (None, None)
        else:
            Wf = max(Xf) - min(Xf)
            Wr = max(Xr) - min(Xr)
            if length_mode == "front":
                Wt = Wf
            elif length_mode == "right":
                Wt = Wr
            elif length_mode == "mean":
                Wt = (Wf + Wr) / 2.0
            else:
                Wt = min(Wf, Wr)
            LfRf = _best_pair_near_width(Xf, Wt)
            LrRr = _best_pair_near_width(Xr, Wt)
            Lf, Rf = LfRf if LfRf else (min(Xf), max(Xf))
            Lr, Rr = LrRr if LrRr else (min(Xr), max(Xr))

    return {
        "y_top": y_top,
        "Lf": Lf, "Rf": Rf,
        "Lr": Lr, "Rr": Rr,
        # 闂傚倷鑳堕、濠傗枖濞戞粌顤傞梻渚€鈧偛鑻晶顖滅磼椤旇偐孝闁靛棙甯￠幊婊冣枔閹稿海鏆繝纰樻閸ㄧ増寰勯悢纰辨晣闁靛繒濮锋鍥⒑缁洍鍋撳畷鍥╃暰闂佺顑嗛幐鎼佸煘閹达箑閱囬柣鏃傚劋濞?key 闂備焦鐪归崺鍕垂閻ｅ瞼涓嶉柟瀛樼贩濞差亜鍐€妞ゆ挾鍋涢崑宥嗙箾閺夋垵鎮戦柣鐔濆懐鐭嗗璺侯焾閳ь剚甯掗～婵嬵敇閻橆偅顫嶉梻浣筋嚃閸犳銆冮崼銏☆潟?correct_paired_horizontals_rest 闂備浇宕垫慨鎾箹椤愶附鍋柛銉㈡櫆瀹曟煡鏌涢幇銊︽澓濞存粍绮撻弻銈囩矙鐠恒劎绠掑銈嗘尪閸ㄥ湱鐥閺屾盯鍩勯崘顏佹濠电偛鎳岄崹浠嬪蓟?
        "front_top_key": _highest_horizontal_key(front_horizontal),
        "right_top_key": _highest_horizontal_key(right_horizontal),
    }


def expand_to_top_span(
    front_support: CoordDict, right_support: CoordDict,
    front_support_models: List[Line], right_support_models: List[Line],
    y_top: float, Lf: float, Rf: float, Lr: float, Rr: float,
    unify_bounds: bool = True,
    round_to_int: bool = False,
    y_round_to_int: bool = False
) -> Tuple[CoordDict, CoordDict]:
    """
    闂傚倷绶氬鑽ゆ嫻閻旂厧绀夐悗锝庡墯瀹曞弶鎱ㄥΟ鎸庣【缂佺姵婢橀湁闁挎繂妫涢妶鎾煕鐎ｎ偅灏い顓滃姂瀹曟﹢濡搁妷锔诲悑缂傚倸鍊搁崐鐑芥嚄閸洖绐楃€广儱娲ㄩ崡姘舵煙缂併垹鏋涢柣蹇氭珪缁绘繈妫冨☉姘杸闂佷紮缍€娴滎剟鍩€椤掆偓缂嶅﹤顭囬懡銈囦笉闁硅揪绲绘禍褰掓煙闂傚顦︾紓浣叉櫆閵囧嫰寮介妸褉濮囬柣搴㈣壘閵堟悂寮婚敓鐘茬＜婵炴垶姘ㄩ悡鍌炴倵閸︻収鐒鹃柛姘儑缁瑦寰勬繝搴℃倯闂佸憡渚楅崢鍓х矓椤曗偓濮婂搫效閸パ冾瀳闁诲孩鍑归崜姘跺疾閸洘鍋愰悹鍥皺椤斿矂姊鸿ぐ鎺戜喊濞存粎鍋ら幃鐑藉箻缂佹鍙嗗┑鐐村灦椤洭鎮為幖浣圭厱闁挎繂娴傞悞鐐亜閺囩喓鎳囩€规洦鍋婂畷鐔碱敂閸♀晛鏁搁梻鍌欑閹诧繝鎮烽妸銉㈡瀺闁哄洨鍋戦埀顒佸浮閹虫粓妫冨☉姘辩嵁闂備礁鎼粙鍕⒔閸曨偀鏋嶉柣妯肩帛閻撴盯鏌嶈閸撶喖銆佸☉妯锋婵炲棗娴氭导鏍⒒娴ｇ懓顕滅紒瀣灦缁轰粙寮埀顒傛崲濞戙垹鐐婃い鎺嗗亾缂佲偓閸岀偞鍋ｉ柧蹇曟嚀閸斿妫?y_top 婵犵數濮伴崹鐓庘枖濞戞埃鍋撳顐㈠祮闁糕斁鍋撳銈嗗笂濡炴帗绂嶉姀銏㈢＜?(Lf,Rf)/(Lr,Rr)闂?
    """
    if not front_support or not right_support:
        return front_support, right_support

    ys = [p[1] for seg in front_support.values() for p in seg] + \
         [p[1] for seg in right_support.values() for p in seg]
    gmin, gmax = (min(ys), max(ys)) if ys else (0.0, 1.0)

    def _extremes(models):
        if len(models) == 1: return models[0], models[0]
        return models[0], models[-1]

    F_left, F_right = _extremes(front_support_models)
    R_left, R_right = _extremes(right_support_models)

    def _rebuild_through(line_model: Line, x_at_y_top: float):
        if line_model.vertical_x is not None:
            x_top = x_at_y_top
            x_bot = x_at_y_top
        else:
            kk = line_model.k
            if kk is None or abs(kk) < 1e-12:
                kk = 1e-12 if (kk or 0.0) >= 0 else -1e-12
            def x_at(y): return x_at_y_top + (y - y_top) / kk
            x_top = x_at(gmin if unify_bounds else line_model.ymin)
            x_bot = x_at(gmax if unify_bounds else line_model.ymax)
        y1 = (gmin if unify_bounds else line_model.ymin)
        y2 = (gmax if unify_bounds else line_model.ymax)
        if y_round_to_int:
            y1, y2 = round(y1), round(y2)
        if round_to_int:
            x_top, x_bot = round(x_top), round(x_bot)
        return [(x_top, y1), (x_bot, y2)]

    front_support = dict(front_support)
    right_support = dict(right_support)

    if Lf is not None and Rf is not None:
        front_support[F_left.id]  = _rebuild_through(F_left,  Lf)
        front_support[F_right.id] = _rebuild_through(F_right, Rf)
    if Lr is not None and Rr is not None:
        right_support[R_left.id]  = _rebuild_through(R_left,  Lr)
        right_support[R_right.id] = _rebuild_through(R_right, Rr)

    return front_support, right_support


def correct_horizontals(
    front_support_models: List[Line], right_support_models: List[Line],
    front_horizontal: CoordDict, right_horizontal: CoordDict,
    skip_front_keys: Optional[set] = None,
    skip_right_keys: Optional[set] = None,
    round_to_int: bool = False,
    front_height_span: Optional[Tuple[float, float]] = None,
    right_height_span: Optional[Tuple[float, float]] = None,
    target_height_span: Optional[Tuple[float, float]] = None,
) -> Tuple[CoordDict, CoordDict]:
    """
    婵犵數鍋涢顓熸叏閹绢喖绠犻幖鎼厛閺佸銇勯弴妤€浜鹃梺鎼炲妽閸庢娊鈥﹂妸鈺佺闁靛ě灞芥杸闂傚倷鑳堕幊鎾诲箹椤愇诲洭鎮界粙璇俱儱鈹戦悩韫抗闁绘梻鈷堥弫鍌炴煕濞戝崬鏋ょ紒澶嬪▕濮婃椽宕ㄦ繝鍛棟濠电偞娼欓崲鏌ュ煝閹捐绠ｉ柨鏇楀亾缂佲偓閸儲鐓冮悶娑掆偓鍏呭缂傚倸鍊哥粔鐢稿垂娴ｅ啰浜芥俊鐐€曠换鎰板箠韫囨洜绀婇柛鏇ㄥ灡閻撳啴鏌曟径娑橆洭缂佺姵鐗曢…鑳槾闁哄拋鍋婇獮鍐箥椤旂粯鍕冮梺绋跨箳閸樠囧绩椤撱垺鈷戠紓浣姑慨澶愭煙閾忣偅灏い鏂跨箻閺屽棗顓奸崨顖ｆТ闂佽崵濮崇粈浣革耿鏉堚晝鐭嗛柛鏇ㄥ灡閻撴洟鏌″畵顔煎濞堝苯顪冮妶鍐ㄥ姎闁挎洦浜滈悾?correct_paired_horizontals 闂傚倸鍊风欢锟犲磻閸涱厙锝夊箳閺冣偓椤愯姤銇勯幇鍫曟闁哄拋鍓欓…鍧楁嚋閻㈢偣鈧帞绱掗埀?
    婵犵绱曢崑鎴﹀磹濞戙垹鏄ラ柡宥庡幗閹酣姊绘担鍛婃儓妞わ富鍨拌灋闁哄啫鍊瑰畷鍙夋叏濡寧纭剧紒鐘虫緲闇夐柨婵嗙墛椤忕娀鏌熼悡搴涘仮婵﹤顭烽崺鈧い鎺戝閸ㄥ倹銇勯弮鍥棄闁逞屽墰閺佸寮婚敐澶娢╅柕澶堝労娴尖偓缂傚倷绶￠崰鎾诲礉閹存繍鍤曠紒瀣儥閻撱儵鏌嶈閸撴稓鍒掗鐔风窞閻忕偞鍎虫禒蹇擃渻閵堝棗濮傞柛搴℃惈鐓ゆい鎺戝閻撶喖鏌嶉崫鍕偓缁樻櫠閿曞倹鐓?
    """
    skip_front_keys = skip_front_keys or set()
    skip_right_keys = skip_right_keys or set()

    fh_keep = {k:v for k,v in front_horizontal.items() if k in skip_front_keys}
    rh_keep = {k:v for k,v in right_horizontal.items() if k in skip_right_keys}
    fh_rest = {k:v for k,v in front_horizontal.items() if k not in skip_front_keys}
    rh_rest = {k:v for k,v in right_horizontal.items() if k not in skip_right_keys}

    fh_rest2, rh_rest2 = correct_paired_horizontals(
        fh_rest,
        rh_rest,
        front_support_models,
        right_support_models,
        round_to_int=round_to_int,
        front_height_span=front_height_span,
        right_height_span=right_height_span,
        target_height_span=target_height_span,
    )
    fh_rest2.update(fh_keep)
    rh_rest2.update(rh_keep)
    return fh_rest2, rh_rest2


# processors.py (闂傚倷绀侀幖顐⒚洪敂閿亾缁楁稑鍟伴弳锕傛煛鐏炶鍔氱紒鐘插暱椤法鎹勬笟顖氬壉闂佹寧绋戦澶愬蓟?enforce_2d_view_symmetry 闂傚倷绀侀幉锟犲垂閸忓吋鍙忛柕鍫濐槸濮?

def enforce_symmetry(support_orig: CoordDict,
                             horizontal_orig: CoordDict) -> Tuple[CoordDict, CoordDict]:
    """
    闂?D闂備浇宕甸崰鎰版偡閵夈儙娑樜旈埀顒勬箒濠碘槅鍨跺Λ鍨柦椤忓牊鐓曠€光偓閳ь剟宕戦悙宸禆闁靛ň鏅滈悡銉︾箾閹寸儐鐒鹃悗姘閳ь剝顫夐幃鍌涚鐠鸿櫣鏆︽慨妯垮煐閸ゅ鏌涢…鎴濅簼婵炲牅鍗冲娲捶椤撶偘澹曢梺鎼炲姀濞夋盯鈥﹂崶鈺€娌柛鎾楀本绁梺鑽ゅЬ濞咃綁宕曢妶鍥ｅ亾濮橆剙绾уǎ鍥э躬椤㈡盯鏁愰崟顓犳晨闂備浇顕栭崰妤冨垝閹炬剚鍤曢柛顐ｆ礀楠炪垽鏌￠崶鈺佹珡闁稿鍔戝铏圭矙鐠恒劎顔囬梺鍛娚戦悧婊堟嚍闁稁鏁嗛柛鏇ㄥ亞椤ρ囨⒑鐠団€崇仭婵犮垺锚閳绘挻瀵肩€涙﹩妫呭銈嗗笒椤︻垱绂嶉悙瀵哥闁割偆鍠庨悘锔剧磼鐎ｎ亶妯€妞ゃ垺锕㈤幃娆撴濞戣鲸鍠橀梻鍌欑劍閹爼宕濆畝鍕９閻犲洩顥嗛搹瑙勫磯闁靛ě鍕剁础?(x=a) 闂備浇顕ч柊锝咁焽瑜嶉敃銏℃綇椤愮喎寰旈梻?
    闂備礁鎼ˇ顐﹀疾濠婂牊鍋￠柕鍫濐槹閻撳倹绻濇繝鍌滃缂佲偓閸曨垱鐓犻柟顓熷笒閸旀粍绻涢崼锝嗙【闂囧鏌涜箛鎾虫倯闁汇劍鍨块弻宥夊Ψ鍠傞幋鐘电煔闁告鍋愰弨浠嬫煕濞戝崬鏋涚€殿喖鐏濋埞鎴︻敊閻ｅ瞼顔囩紓浣藉紦缁瑩鐛崘銊庢棃宕ㄩ鐓庡闂備礁鎲″ú锕傚磿椤忓牜鏁囬柕蹇曞Ь琚濋梻浣烘嚀椤曨參宕戦悙鐢电闁告洦鍊嬭ぐ鎺撳亹闁圭粯甯╅弳銏狀渻閵堝懏绂嬮柛鎾跺枛楠炲啫鈻庨幘铏祶濡炪倖鎸炬慨鐑藉礋濡偐纾肩紓浣靛灩瀵箖鏌涢悩宕囧ⅹ闁挎洏鍨介獮姗€顢欓挊澶樷偓蹇涙⒑閼恒儍顏埶囨导瀵稿彆妞ゆ巻鍋撻懣鎰版煕閵夈劍纭鹃柡瀣枑閵囧嫰骞掗幘鍓佺厜閻庤娲忛崕鏌ュ箚閺冨牊鏅查柛鈩冪懄濞堟悂姊绘担濮愨偓鈧柛瀣尰閵囧嫰寮介妸褉濮囬柣搴㈣壘閵堟悂寮婚埄鍐ㄧ窞濠电姴鍠氬Λ娑樷攽閻愬弶顥撻柛銊ㄦ缁瑦寰勭€ｎ剛鐦堥棅顐㈡处濞叉粓藝?
    濠德板€楁慨鐑藉磻閻愯鑰块柛锔诲幘缁犳棃鏌″鍐ㄥ闁崇粯姊婚埀顒€绠嶉崕杈┾偓姘煎枤缁絽螖閸涱喚鍘?D闂傚倸鍊搁崐鎼佸疮閹惰棄鏄ラ柡宥庡弾閺佸﹦鈧厜鍋撻柍褜鍓熼崺鈧い鎴ｆ硶缁侀攱銇勯銏╂█鐎殿喗濞婇弫鎰板幢濞嗗本鐏冩俊鐐€曠换鎰偓姘煎幘缁宕奸姀鈥虫瀾闂佺厧澹婇崜娆撴倶鏉堚晝纾肩紓浣癸供閻掍粙鏌熼钘夘棆濞寸媴绠撻幐濠冨緞婵犱胶绀嬮梻浣筋嚙缁绘帡宕戦幇鏉跨；闁圭偓鎯屽▓浠嬫煟閹邦垰鐨洪柨娑樼У缁傚秴鈽夐姀锛勫帾?
    """
    if not support_orig and not horizontal_orig:
        return support_orig, horizontal_orig

    print("  - transform step completed")

    # 1. 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晠鏌￠崟顐ょ疄濞存粌缍婇弻鐔煎箚瑜嶉弳杈ㄣ亜閵堝懏鍤囬柟顔煎槻閳诲氦绠涢弮鎴烆棧婵犵數鍋涢悺銊╂晝閵忋倕绠氶柛鎰靛枛缁€瀣亜韫囨挻鎼愭鐐╁亾闂傚倸顭崑鍕洪妶澶婄柈妞ゆ劧闄勯崐鍨亜閹惧崬鐏柛搴￠叄閹鎮藉▓璺ㄥ姼濠?x_center (闂備浇顕ч柊锝咁焽瑜嶉敃銏℃綇椤愮喎寰旈梻?
    all_x = []
    for seg in list(support_orig.values()) + list(horizontal_orig.values()):
        all_x.extend([p[0] for p in seg])
    if not all_x:
        return support_orig, horizontal_orig
    x_center = (min(all_x) + max(all_x)) / 2.0

    support = dict(support_orig)
    horizontal = dict(horizontal_orig)

    # 2. 闂備浇顕х换鎰崲閹邦儵娑樷枎閹捐櫕鐎銈嗘磵閸嬫挻顨ラ悙杈捐€挎鐐差儔閹瑧鈧潧鎽滃皬婵犵數鍋涢顓熸叏妤ｅ啫鏄ラ柡宥庡墮閺嗙偤姊绘担瑙勫仩闁告柨鐭傞、鏍川椤栨浜鹃柛顭戝亞閸欌偓闂佺粯渚楅崳锝呯暦婵傜鍗抽柣鎰蔼缁佹挳姊?
    s_models = build_support_models(support)
    if not s_models:  # 婵犵數濮烽。浠嬪焵椤掆偓閸熷潡鍩€椤掆偓缂嶅﹪骞冨Ο璇茬窞濠电偟鍋撻悡銏ゆ⒑閺傘儲娅呴柛鐕佸灣缁骞掑Δ浣哄幐闂侀€炲苯澧存い銏＄☉閳藉鈻庤箛锝勭椽闂傚倷绀侀幖顐λ囬姣兼稓鈧潧鎲￠～鏇熺節闂堟侗鍎忕紒顐㈢Ч閺岋絽螣閾忕櫢绱為梺闈涙閿曪妇妲愰幘瀛樺闁割偅绻冮崳浠嬫煛?
        return support, horizontal

    pairs = {}
    unpaired_ids = []
    left, right = 0, len(s_models) - 1
    while left < right:
        pairs[s_models[left].id] = s_models[right].id
        pairs[s_models[right].id] = s_models[left].id
        left += 1
        right -= 1
    if left == right:
        unpaired_ids.append(s_models[left].id)

    # 3. 闂備浇顕х花鑲╁緤婵犳熬缍栧鑸靛姇閺嬩焦銇勯弴妤€浜惧Δ鐘靛仦閿曘垽鐛€ｎ喗鍊烽悗闈涙憸灏忔繝鐢靛仜椤曨厽鎱ㄩ幆褉鏋栨繛鎴烇供閸熷懘姊洪鈧粔瀵哥矆閸℃稒鍋ｉ柛婵嗗閹牏鎲搁幍顔夹㈤棁?x_center 闂備浇顕ч柊锝咁焽瑜嶉敃銏℃綇椤愮喎寰?
    processed_supports = set()
    for l_id, r_id in pairs.items():
        if l_id in processed_supports or r_id in processed_supports:
            continue

        l_model = next(m for m in s_models if m.id == l_id)
        r_model = next(m for m in s_models if m.id == r_id)

        # 闂傚倷绀侀幖顐﹀磹閸︻厼鍨濋幖绮规閸熷懎鈹戦崒婊庣劸闁活厽顨婇弻鈥崇暤椤斿吋澶勯悘蹇旂懇濮婅櫣绮旈崱妤€鏆炵€瑰憡绻勭槐鎺楊敋閳ь剟藟閹捐鐒垫い鎺戝€归弳鈺呮煙閾忣偅宕岄柛鈹惧亾?
        if l_model.k is not None and r_model.k is not None:
            avg_k_mag = (abs(l_model.k) + abs(r_model.k)) / 2.0
            new_lk, new_rk = -avg_k_mag, avg_k_mag
        else:  # 婵犵數鍎戠徊钘壝洪敂鐐床闁告劦浜栭崑鎾诲垂椤愶綆妫冮悗瑙勬礀缂嶅﹤鐣烽幒鎴叆闁告洦鍘奸崵閬嶆⒒娴ｈ櫣甯涙い顓炵墦瀹曟椽寮介鐐靛姦?
            new_lk, new_rk = l_model.k, r_model.k

        # 婵犵數鍋犻幓顏嗗緤閻ｅ瞼鐭撻柛顐ｆ礃閸?婵犵數鍋為崹鍫曞箹閳哄懎鍌ㄥΔ锝呭暙绾?闂傚倷鑳堕…鍫㈡崲閹版澘鍌ㄩ柡宥庡亯婵?x_center 闂備浇顕ч柊锝咁焽瑜嶉敃銏℃綇椤愮喎寰?
        l_dist = x_center - l_model.x_mid()
        r_dist = r_model.x_mid() - x_center
        avg_dist = (l_dist + r_dist) / 2.0
        new_l_x_mid, new_r_x_mid = x_center - avg_dist, x_center + avg_dist

        # 闂傚倸鍊烽悞锕併亹閸愵亞鐭撻悗闈涙憸绾句粙鏌熼幆褏浜柛瀣崌濡啫鈽夊▎鎺旑攨闁荤偞鍝庨崝鎴﹀蓟閿濆惟闁靛鍎烘禒鎯р攽閻愰潧甯堕柡鍫墰缁骞掗弮鈧畷澶愭煟閹寸儐鐒界紒瀣濮?
        for mid, model, new_k, new_x_mid in [(l_id, l_model, new_lk, new_l_x_mid),
                                             (r_id, r_model, new_rk, new_r_x_mid)]:
            p1_old, p2_old = support[mid]
            y_min, y_max = min(p1_old[1], p2_old[1]), max(p1_old[1], p2_old[1])
            y_mid = (y_min + y_max) / 2.0

            # 婵犵數鍋犻幓顏嗙礊閳ь剚绻涙径瀣鐎殿噮鍋婃俊鑸靛緞鐎ｎ亖鍋撻悜鑺ュ仭婵炲棗绻愰顏堟煟韫囨棏鐒介柍褜鍓氶鏍窗閺嶎偅宕查柟閭﹀墻閸ゆ洟鏌ｉ敐鍛伇濞戞挸绉垫穱濠囧Χ閸涱厽鐏撴繛瀵稿帶閸婂潡寮婚敐澶婄疀妞ゆ梻鍋撳▓锕傛⒒娴ｄ警娼掗柛鏇ㄥ亜椤秹姊?
            if new_k is None or abs(new_k) < 1e-9:  # 闂傚倷鐒﹂幃鍫曞礉瀹€鍕９閻犲洩顥嗛搹瑙勫磯闁靛ě鍕剁础?
                x_at_min, x_at_max = new_x_mid, new_x_mid
            else:
                x_at_min = new_x_mid + (y_min - y_mid) / new_k
                x_at_max = new_x_mid + (y_max - y_mid) / new_k
            support[mid] = [(x_at_min, y_min), (x_at_max, y_max)]

        processed_supports.add(l_id)
        processed_supports.add(r_id)

    # 婵犵數濮伴崹鐓庘枖濞戞埃鍋撳鐓庢珝妤犵偛鍟换婵嬪礃椤忎焦鐏冩俊鐐€栭幐楣冨磻閻旈晲绻嗛柛銉墯閻撴盯鏌嶈閸撶喖銆佸☉妯锋婵炲棗娴氭导鏍⒒娴ｅ憡鎯堟い锔诲灠铻為柡鍌氱氨閺嬪酣鏌曡箛瀣偓鏍疾椤掑嫭鍊堕柣鎰煐椤ュ绱掔拋宕囩獢闁哄本鐩獮鎺楀即閻旀亽鈧劙姊?x 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾寰婇崜褏鐭?x_center
    for mid_id in unpaired_ids:
        p1, p2 = support[mid_id]
        y_min, y_max = min(p1[1], p2[1]), max(p1[1], p2[1])
        support[mid_id] = [(x_center, y_min), (x_center, y_max)]

    # 4. 闂傚倸鍊烽悞锕併亹閸愵亞鐭撻柣銏㈩焾閽冪喎鈹戦悩鍙夋悙闁告垹濞€閺屾盯寮撮妸銉ょ敖缂備焦鍞荤粻鎾诲箖濡ゅ懏顥堟繛鎴炵懆绾偓闁荤偞鍝庨崝鎴﹀蓟濞戙垹鍐€闁靛ě鍐ｆ嫛婵犵數鍋涢悧濠囧垂閸噮鍤曢柕濞炬櫓閺佸秵绻涢幋鐐垫噧妞ゅ繒鎳撻埞鎴﹀煡閸℃浠氶梺閫炲苯澧痪缁㈠弮閸┾偓妞ゆ帒鍊搁崢鎾煛娴ｅ摜肖濞寸媴绠撳畷鎰版偄妞嬪骸璁查梻鍌氬€烽悞锕併亹閸愵亞鐭撻柣銏㈩焾閽冪喎鈹戦悩鍙夋悙缂佺媭鍣ｉ弻锟犲炊閳轰椒绮跺銈冨妽缁嬫帗绌辨繝鍥舵晬闁挎繂瀚惄搴ㄦ⒑鐠団€虫灍缂侇喗鎸搁锝夊醇閺囩偛鑰块梺鍝勬川閸ｃ儵宕?
    new_s_models = build_support_models(support)
    for h_id, h_seg in horizontal.items():
        p1, p2 = h_seg
        avg_y = (p1[1] + p2[1]) / 2.0

        xs_at_y = [m.x_at(avg_y) for m in new_s_models]
        xs_at_y = [x for x in xs_at_y if math.isfinite(x)]
        if not xs_at_y: continue

        x_left_support = min(xs_at_y)
        x_right_support = max(xs_at_y)

        horizontal[h_id] = [(x_left_support, avg_y), (x_right_support, avg_y)]

    return support, horizontal


# ================================
# 闂傚倷绀侀幖顐﹀磹閻熼偊鐔嗘慨妞诲亾鐠侯垶鏌涢幇闈涙灍闁哄拋鍓氶幈銊ヮ潨閸℃顫╃紓浣筋唺缁舵岸寮诲☉銏犵闁哄洨鍋熼崢顐ｇ節閳封偓閸愵€呪偓娈垮枛閻忔艾顕ラ崟顓涘亾閿濆骸浜濇繛鍫滃嵆濮婃椽宕烽鐐板闂佹悶鍔屽鈩冧繆鐎涙绡€闁告洦鍘煎畷銉ヮ渻閵堝棛澧柛鎴濈秺瀹曠敻鎮╁顔藉仴缂傚倷鐒﹂敋濠殿喖鐭傞弻娑㈠Χ韫囨洜鏆ら悗娈垮枤閺佸宕洪埀顒併亜閹哄秶璐版繛鍫燁殕娣囧﹪顢涘顒夋濡炪倖鎸堕崹鍦棯?
# ================================
def align_to_top(support: CoordDict,
                                     horizontal: CoordDict) -> CoordDict:
    """
    闂備浇顕х换鎰崲閹邦儵娑㈠籍閸屾粌宕ラ柣搴㈢⊕椤洭鍩㈤弮鈧妵鍕疀閹惧銈╁┑鐐插悑鐢繝寮诲☉銏犖ㄩ柨鏇楀亾闁告柣鍊濋弻娑㈡倷鐎涙ê鍞夐梺璇″灠閸熸潙鐣烽悢纰辨晢闁逞屽墴閵嗗倿寮婚妷锔惧幐闂佸壊鍋呯换宥呂ｈぐ鎺撶厸濞撴艾娲ゅ▍宥嗩殽閻愯揪鑰挎鐐差儔閹瑧鈧潧鎽滃皬婵犵數鍋涢顓熸叏閻㈢纾块柤娴嬫櫆瀹曞弶淇婇姘倯闁稿锕㈤幃姗€鎮欓悽鐐光偓濠囨煕鐎ｎ偅灏い顓滃姂瀹曠喖顢楁担鍦婵犵绱曢崑鎴﹀磹閺囥垺鍊堕柛顐犲劚閻掑灚銇勯幒宥堝厡缂佺姵鎸婚妵鍕晜鐟欏嫭鐝氶梺璇″枛閻栫厧鐣烽柆宥呯疀闁靛鍎版竟?

    - 闂傚倷鑳堕幊鎾绘倶濮樿泛纾块柟鎯版閺勩儳鈧厜鍋撻柍褜鍓熼獮澶愬箻椤旂厧鑰垮┑掳鍊撻懗鍫曘€呴鐔虹闁瑰鍋為幆鍕煕濡寧顥夐柕鍡樺浮閹虫粌鈻撻幐搴ｆ毈婵犵妲呴崹浼村触鐎ｎ喗鍋╅弶鍫涘妺缁诲棙銇勯弽鐢靛缂併劌顭烽弻鐔碱敊閻ｅ瞼鐓夐悗娈垮枛閻栫厧鐣烽柆宥呭嵆闁绘洑绀佹禒娲⒒娴ｇ懓顕滅紒瀣灴閹绺界粙璺ㄤ紜濠碘槅鍨伴惃鐑藉磻閹捐埖鍠嗛柛鏇ㄥ枛椤ユ繈姊洪崨濠勬噮婵炶尙鍋ゅ铏圭矓閸℃顏╁┑顔肩墦閺岋綁寮介悽鐢瞪戠紓?y_top_target闂?
    - 闂傚倸鍊风欢锟犲礈濞嗘垹鐭撻柡澶嬪焾閸熷懎鈹戦悩瀹犲缂佺姰鍎甸弻宥堫檨闁告挾鍠庨锝夊垂椤愩垻绐為柣搴秵閸嬪懎鈻撴导瀛樷拺闁革富鍘兼禍楣冩煕閵娿劍纭炬い顓炴川娴狅箓宕滆濞村嫰鏌ｉ悩杈╊槮婵犫偓鏉堚晝鐭嗗璺侯灲鎼淬劌鐐婇柕濞у懐鏆梺璇查閻忔艾螞閸愩劎鏆︽俊銈呭暞瀹曞鏌ц箛娑掑亾濞戞顒㈤梻鍌氬€风欢锟犲窗閹捐绀夐幖鎼厛閺佸倹銇勯幒鎴濐仾闁稿﹦鍏橀弻锝夋偄閸濆嫷鏆柣搴㈢閻擄繝寮婚敓鐘茬＜婵炴垶姘ㄩ悡鍌炴倵閸︻収鐒鹃柛姘儑缁瑦寰勬繝搴℃倯闂佸憡渚楅崢鍓х矓椤曗偓濮?
    - 闂傚倸鍊烽悞锕併亹閸愵亞鐭撻柣銏㈩焾閽冪喎鈹戦悩鎻掝仾濠殿垰銈搁弻銊モ槈濡警浼€闂佸搫妫崜姘跺箞閵娾晜鏅查柛娑卞灣椤撴椽姊绘担绋跨骇缂侇喗鎸搁锝夊Ω閳哄﹥鏅┑鐐村灦閻熴儵顢旇ぐ鎺撯拺闁告繂瀚峰Σ鍛婁繆椤愶絾鐓ラ柍璇查叄婵偓闁靛牆妫楅崜顓㈡⒑閸涘﹥澶勯柛顭戝墴閸┾偓妞ゆ巻鍋撻柨鏇ㄤ邯瀵宕奸妷銉庘晝鎲稿鍕嚤闁稿瞼鍋為悡鐔兼煙闁箑鏋熸い蹇曞枔缁辨帗娼忛妸褏鐣洪梺鐟板槻閹虫ê鐣疯ぐ鎺濇晩闁绘挸娴风紙绫濋梻鍌欒兌椤宕熼銏╂綌闂備胶绮悧顓犲緤閸ф绀嗛柟鐑橆殔缁€鍫㈡喐婢舵劕鐒垫い鎺嶇筏閼拌法鈧娲滈崗姗€鐛箛鏇氭勃闁诡垎鍐潚闂?y_top_target 婵犵數鍋為崹鍫曞箰閹间讲鈧箓宕奸妷銉у姦?

    Args:
        support: 闂備浇宕甸崰鎰版偡閵夈儙娑樜旈埀顒勬箒濠殿喗銇涢崑鎾绘煙椤栨艾鏆ｇ€规洜鍠栭、妤佹媴鐟欏嫷鍞堕梻鍌欑濠€閬嶅磻閹捐鍨傞悹杞拌閻掍粙鎮橀悙鎻掆挃妞も晝鍏橀幃瑙勩偊閹稿寒浠╅梺鍦櫕閸犳牠寮诲☉婊呯杸闁哄啠鍋撻柛瀣█閺?
        horizontal: 闂備浇宕甸崰鎰版偡閵夈儙娑樜旈埀顒勬箒濠殿喗銇涢崑鎾绘煙椤栨艾鏆ｇ€规洜鍠栭、鏍倻閸℃绫嶉悗瑙勬磸閸庣敻鐛€ｎ喗鍊烽悗闈涙憸灏忔繝鐢靛仜椤曨厽鎱ㄩ幆褉鏋栨繛鎴欏灪閸嬨倗鎲搁弬璺ㄦ殾婵°倕鎳庣粻褰掓煟閹般劍娅呭ù?

    Returns:
        婵犵數鍎戠徊钘壝归崒鐐茬獥婵°倕鎷嬮弫鍡樼節婵犲倻澧曢悷娆欑畵楠炴牗娼忛崜褏蓱闂佷紮缍佹禍鍫曞蓟閿熺姴鐒垫い鎺戝閺佸秵绻涢幋鐐垫噧妞ゅ繐缍婂娲传閸曞灚笑濠碘槅鍋呴弻銊╁煝鎼淬劌顫呴柍鍨涙櫅娴滅偓绻涢幋鐐垫噽婵炲牊妫冮弻娑橆潩閿濆懍澹曢梻?
    """
    # 婵犵數濮烽。浠嬪焵椤掆偓閸熷潡鍩€椤掆偓缂嶅﹪骞冨Ο璇茬窞濠电偟鍋撻悡銏ゆ⒑閺傘儲娅呴柛鐕佸灣缁骞掑Δ浣哄幐闂侀€炲苯澧存い銏＄☉閳藉鈻庤箛锝勭椽闂傚倷鑳堕幊鎾绘偤閵娾晜鍋嬫俊銈呮噺閹酣姊绘担鍛婃儓妞わ富鍨拌灋閻庨潧鎲￠～鏇熺節闂堟侗鍎忕紒鈧崱妯肩闁糕剝锚婵牓鏌ㄩ悢鏉戝姦婵﹤顭峰畷鍫曟晲閸涱剙顥氭繝鐢靛О閸ㄧ厧鈻斿☉姘ｅ亾濮樼厧娅嶆?
    if not support or not horizontal:
        return support

    # 1. 闂傚倷鑳堕幊鎾绘倶濮樿泛纾块柟鎯版閺勩儳鈧厜鍋撻柛鏇ㄥ亜閻濇﹢姊洪柅鐐茶嫰婢ь垱銇勯妸銉︽悙閾伙絾顨ラ悙瀛樸仧闁告瑥鍟锝夊醇閺囩偛鑰垮┑鐐叉閸旀寮抽悤鎶芥⒒娴ｄ警娼掗柛鏇ㄥ亜椤秹姊?
    top_y, top_key = None, None
    for hid, seg in horizontal.items():
        y_mean = (seg[0][1] + seg[1][1]) / 2.0
        if top_y is None or y_mean < top_y:
            top_y, top_key = y_mean, hid

    # 婵犵數濮烽。浠嬪焵椤掆偓閸熷潡鍩€椤掆偓缂嶅﹪骞冨Ο璇茬窞闁归偊鍓欓悵妯侯渻閵堝懐绠版繛灞傚€濆畷銏ゅ箻椤旂晫鍘甸梺鍓茬厛閸嬪嫰宕濋妶澶嬬厱闁宠桨鑳堕悞鍝モ偓娈垮枤閺佸宕洪埀顒併亜閹哄秶璐版繛鍫燁殕娣囧﹪顢涘顒夋濡炪倖鎸堕崹鍦棯瑜旈弻娑㈠煡閸℃绠荤紓浣插亾濠㈣泛艌濡插牓鏌￠崘銊モ偓鎼佸几閺冣偓缁绘盯骞撻幒鎾充淮濡ょ姷鍋炵敮鈩冧繆閻戣棄惟鐟滃繘顢欐径鎰拺?
    if top_key is None:
        return support

    # 闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鐐窞閺冨牆纾兼繛鎼墯閸ㄥ潡骞栭鐐粹拺闁告繂瀚峰Σ鍛婁繆椤愶絿鈽夐柍缁樻崌楠炲牓顢旈崼鐔哄幈閻熸粌閰ｅ畷婵嬪冀椤撶喎浜梺鎸庣箓濞诧綁鎮炴繝鍥х骇闁割偅绋戞俊鐣岀箔閹达附鈷戦柣鐔稿閹界娀鏌涢妸銉ユ毐妞ゎ厹鍔戦獮瀣晜閽樺澹勯梻浣告啞濞诧箓宕㈤悾宀€鐜绘俊銈呮噺閻撴稓鈧箍鍎遍幊蹇涘窗濮椻偓閺岋絽鈹戦幇顒佺亶闂?
    y_top_target = (horizontal[top_key][0][1] + horizontal[top_key][1][1]) / 2.0

    # 2. 闂傚倸鍊风欢锟犲礈濞嗘垹鐭撻柡澶嬪焾閸熷懎鈹戦悩铏殤鐎规挷绶氶弻锟犲醇濠靛牅绮甸梺鍛婄懃缁绘垿骞堥妸銉㈡斀闁规儳澧庤摫濠电姭鎷冮崘顎呪偓娈垮枛閻忔艾顕ラ崟顓涘亾閿濆骸浜濇繛鍫滃嵆濮婃椽宕烽鐐板闂佹悶鍔忓▔娑⑩€﹂崶鈺€娌柛鎾楀本绁?
    new_support = {}
    for gid, seg in support.items():
        p1, p2 = seg

        # a. 闂備浇宕垫慨鏉懨洪妶鍛傛稑螖閸涱厽妲梺绯曞墲钃遍柛搴ｅ枛閺岋繝宕堕妷銉т患闂佸憡鏌ｉ崕鐢稿蓟濞戞﹩鐓ラ柛鎰典簽閸旑垶姊洪棃娑欘棞闁挎洦浜濠氬醇閵夈儙鈺冩喐濠婂嫬顕遍柛宀€鍋為悡?(Y闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾寰婇幆褜鍤楅柛鏇ㄥ櫘濡叉儳鈹戦悙鑼闁搞劌澧庣划娆愬緞閹邦兛绱堕梺鍛婃处閸樼儤绂嶉姀銈嗏拻?
        if p1[1] > p2[1]:
            p_bottom, p_top = p1, p2
        else:
            p_bottom, p_top = p2, p1

        # b. 闂佽娴烽崑锝夊磹濞戞ǚ鏋嶉柨婵嗩槹閸嬬喐绻涢幋娆忕仾闁稿骸閰ｉ幃妤呮偨濞堣法鍔稿┑鐐茬墢婵灚绌辨繝鍥舵晬婵＄偠顕ф禍鍓р偓瑙勬礀濞茬娀宕戦幘缁樼叆閻庯綆鍓﹀ù鍕⒑闂堟侗妲堕柛濠冾殘缁粯绂掔€ｎ偆鍘甸梻鍌楀亾闁归偊鍠栨俊浠嬫⒑閸濆嫷鍎岄柡鍛█楠?
        line = Line(p1, p2, str(gid))

        # c. 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晛鈹戦悩瀹犲闁圭懓鐖奸弻鏇熺箾瑜嶇€氼噣鎮伴妷鈺傗拺闁告繂瀚瓭濠电偛妯婇崣鍐箖閻㈠壊鏁婇柤鎭掑劚閸斿懎顪冮妶鍌涙珖闁告搩妲p_target婵犵數濮伴崹鐓庘枖濞戞埃鍋撳鐓庢灈闁崇粯鎹囬獮瀣晝閳ь剙螞濮椻偓閺岋綁濡搁敃鈧ù顔锯偓瑙勬礃閹倿鐛崶顒夋晣闁绘灏欐导?
        # 婵犵數濮烽。浠嬪焵椤掆偓閸熷潡鍩€椤掆偓缂嶅﹪骞冨Ο璇茬窞闁归偊鍓欏宄邦渻閵堝棛澧慨妯稿姂閸┾偓妞ゆ帒顦顕€鏌熼姘伀闁逞屽墰閺佹悂鈥﹂崼婵冩灁闁绘绮悡銉︾箾閹寸儐鐒芥俊鍙夘殜濮婅櫣绮旈崱妤€顏╁┑顔肩墦閺岋綁寮介悽鐢瞪戠紓浣割儏椤︻垶顢樻總绋垮窛妞ゆ挾濮疯ⅵ
        if line.vertical_x is not None:
            new_top_x = line.vertical_x
        else:
            new_top_x = line.x_at(y_top_target)

        # d. 闂傚倷绀侀幉锛勬暜濡ゅ啰鐭欓柟瀵稿Х绾句粙鏌熼幑鎰靛殭婵☆偅锕㈤弻鐔封枔閸喗鐏嶉梺浼欑到瀹曨剟鈥旈崘顔嘉ч柛娑卞灠閻撶喖姊虹粙鍧楊€楁い鏇ㄥ幘閸掓帡鍩￠崪浣规櫖濠电姴锕ら崯鈺呭礌?
        p_top_new = (new_top_x, y_top_target)

        # e. 婵犵數鍎戠徊钘壝洪敂鐐床闁稿瞼鍋為崑銈夋煏婵犲繐顩柍鐟扮У閵囧嫰寮崒婊勬啒闂佸憡鏌￠崑鎾绘⒒娴ｅ憡鍟為柤瑙勫劤闇夌€瑰嫭澹嬮弸鏃堟煙鏉堝墽鐣辩紒鐙欏洦鐓曢柍鈺佸暞缁€鍐┿亜?
        new_support[gid] = [p_top_new, p_bottom]

    return new_support

# ====== Reconstruct3D (闂?reconstruct3d.py) ======
# reconstruct3d.py 闂?婵犵數鍋為崹鍫曞箰閹间絸鍥础閻愬啫閰ｉ、姘跺焵椤掑嫬钃熼悘鐐电摂閸氬鏌涘☉鍗炵仯濠㈣泛瀚槐鎾存媴閸濆嫅锝嗐亜閵娿儲顥犳繛?
from typing import Dict, List, Tuple, Optional
import math

# 缂傚倸鍊风欢锟犲磻婢舵劦鏁嬬憸鏃堝箖濡ゅ懏鍊婚柦妯侯槺椤︻偄顪冮妶鍡楀闁搞劍妞藉畷鎰暦閸ワ絽浜鹃柣鐔哄閸熺偟鎲搁弶鍨殭闁挎洏鍨介、鏃堝醇濠靛浂妫熼梻浣规偠閸庡姊介崟顖ｆ晝闁伙絽澶囬崑鎾斥枔閸喗鐏€闂佺顑嗛幐鎼佲€﹂崸妤佸殝闁割煈鍋嗙粙鍥⒑娴兼瑧鎮奸柛瀣尵缁?

# ------------- 闂傚倷绀侀幖顐﹀磹缁嬫５娲晝閸屾銉╂煕鐏炴儳鐒归柡瀣墵閺岋繝宕堕張鐢垫晼缂備焦鍔栭〃濠傤潖?/闂?闂備浇宕甸崰鎰版偡閿旂偓鏆滈柟鐑樻煛閸嬫挾鎲撮崟顐熸灆閻庢鍠曢崡鎶藉箖閳哄懏鍤戞い鎺嶇贰閸熷懘姊绘担鐟邦嚋缂佸鍨块幃褔宕ㄩ婊咁槸濠殿喗銇涢崑鎾绘煙椤栨艾鏆ｇ€规洜鍠栭、鏇㈡晲閸ヨ埖鐤梻鍌欒兌椤牆霉濮樿泛绀堟繛鍡樺灦椤洟鏌ㄩ悢鍝勑ｉ柡?-------------

def _mid(ptA: Coord, ptB: Coord) -> Tuple[float,float]:
    return ((float(ptA[0]) + float(ptB[0]))/2.0, (float(ptA[1]) + float(ptB[1]))/2.0)

def _clip(v: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))

def _select_top_horizontal(view_h: CoordDict, axis: str = "x") -> Optional[Tuple[Coord, Coord]]:
    """
    闂傚倷绀侀幉锟犳偡閿曞倹鍋嬮柟杈剧畱閻掑灚銇勯幒宥堝厡闁活厼顑嗙换娑㈠箻閻熸壆鍘銈冨妼濞层倛鐏掗柣蹇撶箣缁€浣圭閻愵剛绡€闂傚牊绋撴晶娑㈡煟閿濆牓鍝哄ǎ鍥э躬椤㈡盯鏁愰崟顓犳晨闂備浇顕栭崰妤冨垝閹炬剚鍤曢柛顐ｆ礀楠炪垽鏌￠崶鈺佹珡闁稿鍔戝娲箰鎼达絺妲堝┑?闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鍓х帛閸婂爼鐓崶銊﹀磳闁绘稒绮庣槐鎺撴綇閵娿儱鎽甸梺杞扮缁夋挳鍩ユ径濠庣叆闁告侗鍨奸崬褰掓⒒娴ｈ鍋犻柛搴㈠▕瀹曟垵鈽夊▎鎴旀灆闂婎偄娲︾粙鎴︽儗濡ゅ啠鍋撶憴鍕婵炴潙鍊圭€靛ジ宕掗悙瀵稿幗闂佸綊鍋婇崰妤咁敂閻旇櫣纾奸弶鍫涘妿閹冲洦顨?x/y 闂傚倷绀佸﹢閬嶅磿閵堝洦鏆滈柟鐑樻婵櫕銇勯幘鍗炵仾闁?
    axis = 'x' 闂傚倷鐒﹀鍨焽閸ф绀夐悗锝庡墲婵櫕銇勯幒鍡椾壕濡炪値鍋侀崹浠嬪极閹邦厼绶為悗锝庡亖閳ь剙鍟村?y' 闂傚倷鐒﹀鍨焽閸ф绀夐悗锝庡墲婵櫕銇勯幒宥堝厡闁荤喎婀遍幉鎼佸棘濞嗗墽鍔?
    """
    if not view_h:
        return None
    items = list(view_h.items())
    # 婵犵數鍋涢顓熸叏娴兼潙纾块柟鍓佺摂閺佸倹銇勯幒鎴濐仾闁?z 闂傚倷鐒﹂惇褰掑礉瀹€鈧埀顒佸嚬閸撶喖寮婚敃鍌氱厸闁告侗鍙冮弫婊堟⒑閹肩偛鍔€闁告劏鏅濋埀顒夊亰閺岋絾鎯旈妶搴㈢秷闂佺硶鏅涢崯鎾春閳ь剚銇勯幒宥堝厡闁活厽甯￠弻锝呪攽閹邦剚鐏嶉梺璇″灡濡啴寮崒鐐茬濠㈣泛锕ｆ竟?
    items.sort(key=lambda kv: (kv[1][0][1] + kv[1][1][1]) / 2.0)  # z 闂備浇顕х换鎰崲閹邦収娈介煫鍥ㄦ礃椤洘绻涢崱妯诲碍闁告纾槐鎾诲醇閵忕姌銉╂煟閻旂濮嶉柡灞诲妼閳藉顫滈崱妯烇箑鈹戦悩顐壕濡炪倕绻愰悧鍡欑矆?
    seg = items[0][1]
    (xa, za), (xb, zb) = (seg[0], seg[1])
    if axis == "x":
        return ( (xa,za), (xb,zb) ) if xa <= xb else ( (xb,zb), (xa,za) )
    else:  # axis == 'y'
        ya, yb = xa, xb  # 闂備礁鎼ˇ顐﹀疾濠婂牊鍋￠柍鍝勬噹闂?seg 婵犵數鍋為崹鍫曞箹閳哄懎鍌ㄩ柟顖嗏偓閺嬫棃鏌熺€电啸缂佺姵姊归妵鍕箣閿濆棛銆婂銈呯箰瀹曨剟鍩ユ径鎰闁告剬鍛晨闂備礁鎲¤摫闁瑰憡鍎冲嵄闁规壆澧楅崑鎰版煣韫囷絽鈧?y闂傚倷鐒︾€笛呯矙閹达附鍋嬮柛娑欐綑閻ら箖鏌涢锝嗙妞ゃ儱鐗撻弻鏇＄疀閺囩倫锝囩磽瀹ュ懐绠婚柡灞糕偓鎰佸悑闁告侗鍠栭ˇ鈺佲攽?(y,z) 闂?
        if ya <= yb:
            return ( (xa,za), (xb,zb) )
        else:
            return ( (xb,zb), (xa,za) )

def _bottom_from_support(view_support: CoordDict, axis: str = "x") -> Optional[Tuple[Coord, Coord]]:
    """
    婵犵數鍋涢顓熸叏鐎垫瓕濮抽柤娴嬫櫆閸嬫牠姊洪鈧粔鎾礃閳ь剟鏌ｉ悢鍝ユ噧閻庢凹鍙冨鍐差煥閸喓鍘甸梺缁樺姦閸撴瑩鎮橀埡鍌滅闁割偆鍠庨悘鎾煕閵婏箑鍔ゆい顓滃姂瀹曠喖顢栫捄銊ョ婵犵數鍋犻幓顏嗗緤閽樺褰掓倻缁涘鏅滃銈嗗笒鐎氼參宕愰悜鑺ョ厱闊洦鎼╁Σ鎾煕鐎ｎ偅灏柍瑙勫灴瀹曘劑寮堕崹顔剧暠闂傚倸鍊风欢锟犲磻閸曨垁鍥敍閻愭彃鎯炲銈嗘尵閸犳捇鍩㈤弮鍫熷€甸柨婵嗙凹缁ㄨ棄菐閸ャ劍銇濋柡宀嬬秮婵℃悂濡烽妷顔绘偅濠电偞鍨堕弻銊ф崲濡櫣鏆﹂柨婵嗘噽閺嗭箓鏌涢妷锔芥瀯缂佽鲸鎹囧铏圭磼濡搫顫庡┑鐐叉噷閸ㄨ危閹邦兘鏋庨柟鎯х－椤?x/y 闂傚倷绀佸﹢閬嶅磿閵堝洦鏆滈柟鐑樻婵櫕銇勯幘鍗炵仾闁?
    """
    if not view_support:
        return None
    bottom_pts: List[Coord] = []
    for seg in view_support.values():
        (x1,z1),(x2,z2) = seg
        # 闂傚倷绀侀幉锟犳偡閿曞倹鍋嬮柟杈剧畱閻掑灚銇勯幒宥堝厡闁活厼妫涚槐鎾愁吋閸涱噮妫ょ紓渚囧枓閺呯娀銆佸☉姗嗙叆闁告剬鍐嚙闂傚倷鑳堕崑銊╁磿閼碱剚宕查柟閭﹀枟椤洘淇?闂傚倷绀侀幉锛勫枈瀹ュ鍨傜€规洖娲ㄧ粻鏃堟煕濞戝崬鏋ら柍缁樻閺岋綁骞嬮悜鍥︾返闂佸憡鏌￠崑?=> 闂?z 闂備礁鎼ˇ顖炴偋閸℃稑鐤い鎰剁畱妗呴梺鎼炲労閸撴岸宕曞澶嬬厱闁哄洢鍔屽鎯归悡搴♀偓鍧楀蓟閿濆绠涙い鏃傜摂娴犙呯磽?
        if float(z1) >= float(z2):
            bottom_pts.append((float(x1), float(z1)))
        else:
            bottom_pts.append((float(x2), float(z2)))
    if len(bottom_pts) < 2:
        return None
    # 闂?x 闂?y 闂傚倸鍊风欢锟犲磻閸曨垁鍥敃閿曗偓閻掑灚銇勯幒宥堝厡闁活厼顑嗙换娑㈠箻鐟欏嫮銆愬?闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鍓х帛閻撴洘绻涢崱妯哄闁诲繘浜堕弻?
    if axis == "x":
        bottom_pts.sort(key=lambda p: p[0])  # x
    else:
        bottom_pts.sort(key=lambda p: p[0])  # 婵犵數鍋為幐濠氭儍濠婂牆鐐婇柕濠忚礋閳ь剙鍟撮弻锝嗘償閵忊懇濮囧銈庡幖濞层倝鍩㈤幘璇茬闁挎洍鍋撻柛?(y,z)闂傚倷鐒︾€笛呯矙閹达箑瀚夋い鎺戝閺佸棙绻濋棃娑欐悙缂?p[0] 闂?y
    left, right = bottom_pts[0], bottom_pts[-1]
    return (left, right)



def extract_bases_front(front_support: CoordDict, front_horizontal: CoordDict):
    """
    婵犵數鍎戠徊钘壝归崒鐐茬獥婵°倕鎷嬮弫鍡樼節婵犲倻澧涢柛?V2闂傚倷鐒︾€笛呯矙閹烘鍎楁い鏂垮⒔缁犳柨顭跨捄渚剳妞も晝鍏橀弻娑樷槈閸楃偛顫╅梺瀹狀嚙缁绘﹢寮婚敐澶涚稏妞ゆ巻鍋撳┑鈥茬矙閺屸剝绗熼崶褎鐝濆Δ鐘靛仦閿曘垽鐛€ｎ喗鏅滈悶娑掆偓鍏呭婵犵數濮村ú锕傚磹閻戣姤鐓熺憸宥夊箺濠婂懐鐭嗗鑸靛姇缁狙囨煃閸濆嫪绱栨い蹇撶叒閻戣棄绀冩い鏃囧亹椤︻噣姊虹紒姗堜緵闁哥姵甯″畷鎴﹀箻鐠囪尙鐤€濡炪倕绻愬ú銈夌嵁閳ь剟姊绘繝搴′簻婵炲眰鍊濆畷顖烆敃閿旂粯鏅銈嗘⒒閻℃棃鎮楅弻銉︾厵闂侇叏绠戦悘锝囩磼閻樺磭澧紒缁樼箖缁绘盯宕归鐟颁壕闁硅揪绠戦悞鍨亜閹哄秶顦﹂柣蹇曞枛閺?
    闂傚倷绀侀幉锟犲箰鐠囧弬娑㈠礃閵娿垺鐎洪柟鍏肩暘閸斿瞼澹曟繝姘卞彄闁搞儯鍔嶆径鍕煟鎼淬垹绲婚柍瑙勫灦瀵板嫮鈧綆鍋掑鍧楁⒒閸屾鍫ュ疾濠婂懐鐭欏鑸靛姦閺佸洭鏌ｉ幇鐗堟锭妞も晩鍓熼弻鈩冨緞鐏炴垝鎴峰銈冨劜閸旀骞戦姀銈呯闁冲搫鍊峰锕€鈹戦悩璇у伐闁瑰啿绻橀幃楣冩焼瀹ュ棛鍘遍梺鎸庣箓缁ㄨ偐鑺辨禒瀣厱閻庯絽澧庣粔顕€鏌℃担鍝バх€规洜鍘ч埞鎴﹀箛椤撶喐鍊烽梻鍌氬€搁崐鐢稿磻閹剧粯鐓欑紒瀣硶閻﹀秵銇勯幘鍗炵仼缂佺媭鍨堕弻娑樷槈閸楃偟浼囨繛瀵稿帶閸婂潡寮婚敐澶婄疀妞ゆ梻鐡旀禒褏绱撴担浠嬪摵鐎光偓閸涘﹣绻?
    """
    # 1. 闂傚倷绀侀崥瀣磿閹惰棄搴婇柤鑹扮堪娴滃綊鏌涢妷锝呭闁稿海鍠栭弻锟犲炊閵夈儳浠奸梺鍛婃煟閸庣敻寮诲☉銏犵厸濞达綀顫夐崕鎾绘⒑闂堚晝绉甸柛銊ョ埣楠?
    bottom = _bottom_from_support(front_support, axis="x")
    if bottom is None:
        return None
    (x4, z4), (x3, z3) = bottom  # bottom 闂傚倷绀侀幉锟犲垂閸忓吋鍙忛柕鍫濐槸濮规煡鏌ｉ弬鎸庡暈濞存嚎鍊濋弻锟犲磼濞戞﹩鍤嬬紓浣插亾闁逞屽墴閹宕烽褏鍔搁悗娈垮枛婢у酣寮鈧獮妯尖偓娑櫭崝鍛存椤愩垺鍌ㄩ柛搴＄－缁絽螖閸愶絽浜剧憸鐗堝笚娴溿倗绱撻崒娑欑殤缂?4), 闂傚倷绀侀幉锟犳偡閵夆晛鍌ㄩ柡宥庡亞缁?3)
    
    # 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晝绱撴担鑲℃垿宕曢悢鍏肩厸闁搞儯鍎遍悘鈺呮煕閺傝鍔氶柍钘夘樀楠炴瑩宕橀妸銉ь啇缂傚倷绀侀幖顐ｆ櫠娴犲鍎?X 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾绱炴担鍝ユ殾妞ゅ繐妫斿▽顏堟煟閿濆懎顨欏ù婧垮灲濮婄粯绗熼崶褎鐏侀梺鍛婃煥閻倿銆佸▎鎾崇睄闁逞屽墴楠?
    bottom_center_x = (x3 + x4) / 2.0
    bottom_width = abs(x3 - x4)
    
    # 2. 闂傚倷娴囬妴鈧柛瀣崌閺屾盯顢曢敐鍡欘槰闂佽壈灏欐繛鈧柡宀€鍠撻崰濠偽熸潪鏉款棜闂傚倷绀侀幖顐︽偋閸℃蛋鍥ㄥ閺夋垶鐎銈嗘磵閸嬫挻顨ラ悙杈捐€挎鐐差儔閹瑧鈧潧鎽滃皬婵犵數鍋涢顓熸叏鐎涙ɑ娅犻幖绮规閺嬫棃鏌熸潏鍓х暠鏉╂繈姊虹憴鍕€滈柛鈺佹喘閸┾偓妞ゆ巻鍋撻柨鏇ㄤ邯楠炲啫鈻庨幘璺虹ウ闁圭厧鐡ㄩ幐鍛婄?
    candidates = []
    for seg in front_support.values():
        (px1, pz1), (px2, pz2) = seg
        # 闂?Z 闂傚倷鑳堕…鍫ユ晝閵婏妇鐝堕柛顐犲灪椤愯姤绻濋棃娑氬闁绘帒锕悡顐﹀炊閵夈儱濮㈢紓浣插亾闁告洦鍨扮痪褔鏌涢锝囩畵闁哄棴缍侀弻锝呪攽閹邦剚鐝濋梺杞扮缁夐潧顕ラ崟顓濇勃闁告挆鍕啅缂傚倸鍊烽悞锕€螞韫囨稑鍨傞柟鎯版绾?
        top_pt = (px1, pz1) if pz1 < pz2 else (px2, pz2)
        candidates.append(top_pt)
            
    if not candidates:
        return None

    # 3. 闂傚倷绶氬褍螞濞嗘挸绀夐柡鍥ュ灩閻鎲搁弮鍫濊摕闁靛ň鏅╅弫濠勭磽娴ｅ顏勵嚕閸喒鏀芥い鏃傛櫕缁犳壆绱掗幓鎺濈吋闁糕斁鍋撳銈嗗笂缁€渚€鎮￠埀顒傜磽娴ｆ垝鍚褎顨呴…鍥ㄧ節濮橆剛鍊為梺闈涱煭缁犳垼顣界紓鍌氬€风粈渚€宕愰悷鎷旓綁骞掗幋顓熷兊闂侀潧艌閺呮粓宕曞澶嬬厱闁哄洢鍔屾禍婵嬫煟濠靛嫬濮傞柡?
    # 闂備浇宕甸崰鎰版偡閵壯€鍋撳鐓庡⒋鐎规洖缍婇、娑㈡倷鐎涙ɑ鐝繝娈垮枟閿曗晠宕滃璺虹９闁靛牆妫涚粻鎯ь熆鐠轰警鍎愮紒鈧崼鐔虹闁割偆鍠庨悘锕傛煏閸パ冾伃鐎规洖銈稿鎾倷閹绘崼鎾绘⒒娴ｈ櫣甯涢柛鏃€顨呴埢宥夊閵忊槅娼熷┑鐘绘涧椤戝懐绮堥崒鐐村仯濡わ附瀵ч妴鍐煟閹烘埊鍔熺紒杈ㄥ浮瀹曟帒鈹戦幇顒佹毌闂備胶鍘ч悘姘跺垂閼测晝涓嶆繛鎴欏灩缁€鍐┿亜韫囨挻鍣介柡鍡欏█閺岋綁鎮╅棃娑樺缂備浇顕х€氫即鍨鹃弽顓炵倞妞ゆ帊鐒﹀▍鏍煟韫囨洖浠╅柛瀣姍閹嘲鈹戠€ｎ亞顔愰柣搴㈢⊕钃辨い銉ユ缁辨帞绱掑Ο鍏煎櫗閻庡灚婢樼€氼垶藝鏉堚晝纾兼い顓熷灥婢ь垶鏌熼娑欘棃鐎殿喗鎸虫慨鈧柣妯诲絻琚氶梻鍌欑閹诧繝銆冮崨瀛樻櫇闁靛牆娲﹂浠嬫煟閹邦喖鍔嬮柛搴＄Ч閺屾盯寮撮妸銉ヮ潾闂佸憡蓱閻熴儵鍩ユ径鎰闁告剬鍛晨闂備線鈧偛鑻晶顔剧磼婢跺本鏆€殿喗濞婇幃銏ゅ礂閸忓吋鐝梻浣稿閸嬩線宕曢煫顓犳槀濠电姵顔栭崰妤冪紦閸ф鍨傞柣鎴炆戦崣蹇涙煕閺囥劌鐏犵紒鈧崱娑欑厽婵°倐鍋撻柣鎿冨亰椤㈡﹢濮€閻樻鍞甸梻浣告啞娓氭宕归崗鐓庮嚤闁稿瞼鍋為悡鐔兼煙闁箑鏋熸い蹇曞枔缁?
    # 闂備浇顕уù鐑藉极婵犳艾鐒垫い鎺嶈兌閵嗘帡鏌ょ憴鍕姢闁宠鍨跺鍕偓锝庡亽濮婂潡姊婚崒姣板牓寮查悩璇叉瀬鐎广儱鎳愰弳鍡涙煕閺囨鏉归柛瀣尰缁绘繈宕堕妸褍濮奸梻渚€娼ч…鍫ュ磿濞差亜鐤€广儱顦粻褰掑级閸繂鈷旈柣锝囨暬閺屽秷顧侀柛鎾村哺閹虫繃銈ｉ崘鈺佷函?<= 闂備礁婀遍崢褔鎮洪妸銉冩椽鎮㈤悡搴ｏ紵闁诲海鏁哥涵鍫曞磻閹捐埖鍏滈柛娑卞櫘濡嫰鏌ｆ惔銈庢綈濠电偛锕ユ穱濠囧箻椤旇偐锛滃┑鐐村灦閻燂箑顭块幒妤佺厽閹艰揪缍嗛弨鐗堜繆椤愩垹顏€?1.5 闂傚倷鑳堕…鍫ユ晝閵堝洨鐭撻柧蹇ｅ亞椤╂煡鏌熼悜姗嗘畷闁抽攱鎹囧Λ鍛搭敃椤愩垹绠诲銈呯箺椤曆囧煡婢舵劕绠绘い鏍ㄧ煯婢规洟姊?
    valid_tops = []
    threshold = (bottom_width / 2.0) * 2.5  # 闂傚倸鍊搁崐鎼佸疮椤愶附鍋嬮柛鈩冪☉閻掑灚銇勯幒鎴濇殭濞存粌缍婂娲敊閼恒儱鍞夐悗娈垮櫘閸嬪﹤顕ｉ崼鏇炲瀭妞ゆ梹顑欓崬褰掓煟鎼达絾鏆柛瀣躬瀹曟澘鈽夐姀鈥冲壄闂佺粯鏌ㄩ崥瀣疾?.5闂傚倷鑳堕…鍫ユ晝閵堝洨鐭撶憸鐗堝笒閻掑灚銇勯幒宥嗙グ濠㈣锕㈤弻锝夊冀瑜嶉。鎶芥煙婵傚摜鐣虹€规洘锚椤斿繘顢欑粵瀣у亾瀹ュ鐓熼幖杈剧稻閸も偓濠电姭鍋撻梺顒€绉寸粻濠氭煕韫囨艾浜圭紒鐘崇懇閺岋繝宕橀妸锕€鏋犻梺缁樻尨閺呮盯婀侀梺鎸庣箓閹冲繘藟閻愮儤鍋ㄦい鏍ㄧ⊕瀹曞本鎱ㄦ繝浣虹煓濠德ゅ煐瀵板嫮鈧綆鍋嗗Σ顏呯節绾版ɑ顫婇柛銊ュ悑缁傚秴鈹戦崶褍鐏?
    
    for pt in candidates:
        dist = abs(pt[0] - bottom_center_x)
        if dist < threshold:
            valid_tops.append(pt)
            
    # 婵犵數濮烽。浠嬪焵椤掆偓閸熷潡鍩€椤掆偓缂嶅﹪骞冨Ο璇茬窞閻庯綆鍋傚锕傛⒑閹肩偛鍔橀柛鏂跨У閹便劑濮€閻欌偓閻斿棗螞閻楀牏绠戠紒銊ょ矙閹顫濋鐔烘闂侀€炲苯鍘哥紒鑼帛缁旂喖宕奸妷銉ユ優閻熸粌绉归崺銏＄鐎ｎ偅娅栭梺鍛婃处閸嬪倿宕犻弽銊х閻庢稒顭囬惌濠冧繆椤愩埄鍤熸俊鍙夊姇閳规垿宕煎鍛⒕闂備礁鎲￠〃鍫ュ磻閻愮數鐭嗛柍褜鍓熷缁樼瑹閸パ傜爱闂佺顑嗛幑鍥蓟濞戙垹绠虫俊銈咃攻濞堛儲绻濋悽闈涗粶婵炲樊鍙冮獮鍐╃鐎ｎ€晠鏌曟径鍫濆姕闁哄鍋撶换婵嗏枔閸喗鐏堝銈嗗灥濞差厼鐣烽幋锔芥櫜濠㈣泛顑嗗▍鏍⒑閸撴彃浜剧紒鏌ョ畺椤㈡棃濡舵径瀣幗闂佸湱鍎ゅú妯兼兜閸撗勫枑闁绘鐗忛崣鈧梺纭呮珪椤ㄥ﹪骞婇悙鍝勎ㄩ敎娲晝閸屾稈鎷洪梺鍦焾濞寸兘骞婇崨顔剧闁割偆鍠庨悘鎾煛娴ｅ摜肖濞寸媴绠撻幊鏍煛閸忊晜鍨甸埞鎴︻敋閸℃瑧蓱闂佸搫琚崝搴ｅ垝濮樿泛鍨傛い鏃囶潐閺佺娀姊洪崨濠傚闁告柨锕畷鎴﹀Ω閳哄倻鍙?
    if len(valid_tops) < 2:
        valid_tops = candidates

    # 4. 闂傚倷绀佸﹢閬嶅磿閵堝洦鏆滈柟鐑樻婵櫕銇勯幘璺盒ュ瑙勫▕閺屸€愁吋鎼粹€茬凹濠电偛鐗炵紞渚€寮?
    # 婵犵數鍋炲娆撳触鐎ｎ喗鏅梻浣告啞钃遍柣鈺婂灦閻?Z (婵犲痉鏉库偓鏇㈠磹瑜版帗鏅梺? 闂傚倷绀侀幉锟犮€冮崨顒兼椽濡堕崶顏勑″銈嗘尪閸ㄦ椽寮查鍕€?闂傚倷鑳堕崕鐢稿疾濠靛鈧箓宕奸妷銉х暫闂佽宕橀褏鐚惧澶嬬厾闁归棿鐒﹀☉褔鏌?X 闂傚倷绀侀幉锟犮€冮崨顒兼椽濡堕崶顏勑?
    valid_tops.sort(key=lambda p: (p[1], p[0]))
    
    # 闂?Z 闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鍓х帛閸婂爼鐓崶銊﹀磳闁绘稒绮庣槐鎺撴綇閵娧勫櫚閻庢鍠氶弫濠氬春閳ь剚銇勯幒宥囪窗婵炲牊顨嗛幈銊ノ旈埀顒勬偋韫囨洜鐭嗛柛鈩冪⊕閻撶喖鏌曟繛鍨姎妞ゅ景鍥ㄥ仩婵ɑ濞婇崫铏圭磼鐎ｎ亶妯€妞ゃ垺妫冨畷鍗烆渻閹冾嚙闂?
    # 缂傚倸鍊搁崐椋庣矆娴ｇ儤宕叉俊銈呭暞瀹曟煡鏌涢幇銊︽珖闁崇粯鏌ㄩ埞鎴︽偐閸欏顦╁┑鈩冦仠閸旀垿寮婚敐澶娢╅柕澶堝労娴煎倻绱撴担绛嬪殭闁哥噥鍋婇垾锕傚Ω閳轰絼褔鐓崶銊︾妞わ富鍣ｉ弻鈩冨緞閸℃ɑ鐝曢梺鑽ゅ暱閺呯姴鐣烽幎鑺ュ€婚柤鎭掑劚閸擃參姊洪崨濠冪８闁告柨顦靛畷鎴﹀箻閹颁胶鍙嗛梺鍛婃处閸忔稓鍒掗娑楃箚闁靛牆鎳庨埀顒傤攰瑜版粓姊洪柅鐐茶嫰婢ь垳绱掔拠鎻掆偓濠氭嚍闁秵鍤戞い鎺嶇閻濅即姊洪棃娑辨闂傚嫬瀚悷褍鈹戦悩缁樻锭妞わ附婢樿灋濞撴埃鍋撶€规洏鍎遍埢搴ㄥ箛閳衡偓缁ㄥ姊洪崜鎻掍簼婵炲弶鐗犲畷婵嬪Ψ閳哄倻鍙嗗┑鐐村灦椤洭鎮為悜鑺ョ厓鐟滄粓宕滃▎鎰檮闁哄啫鍊荤粻鏂款熆閼搁潧濮囬柛娆忥攻閵囧嫰寮介顫钵缂傚倸鍊搁ˇ闈涱潖婵犳艾骞㈡繛鍡楃箰楠炲姊洪悷鏉挎缂佺粯绻堥悰顔锯偓锝庡枛閸愨偓濡炪値鍘奸鎰板矗閸愵喚宓?
    if len(valid_tops) < 2:
        return None
        
    t1, t2 = valid_tops[0], valid_tops[1]
    
    # 缂傚倷鑳堕搹搴ㄥ矗鎼淬劌绐楅柡鍥╁У瀹?t1 闂傚倷绀侀幖顐も偓姘卞厴瀹曞綊鎮ч崼鈶╂灆闂婎偄娲﹀鍦礊閸ヮ剚鐓熺憸宥夊箺濠婂懐鐭嗗┑? 闂傚倷绀侀幖顐も偓姘卞厴瀹曞綊骞忕仦璁虫睏闂佸憡绋戦敃銉х礊?
    if t1[0] > t2[0]:
        t1, t2 = t2, t1
        
    (x1, z1), (x2, z2) = t1, t2

    # --- 闂備浇宕垫慨鎾敄閸涙潙鐤柟鎯板Г閸庡﹥銇勯弽顐粶缂佺姰鍎甸弻鐔煎箚瑜嶉弳杈╃磼?(闂傚倷绀侀幉锟犳偡椤栫偛鍨傞柛顐ｆ礀閻? ---
    # print(f"DEBUG: Bottom Center={bottom_center_x}, Filter Threshold={threshold}")
    # print(f"DEBUG: Rejected pts={[p for p in candidates if p not in valid_tops]}")
    # print(f"DEBUG: Selected Top={t1, t2}")

    return ((float(x1), float(z1)), (float(x2), float(z2)),
            (float(x3), float(z3)), (float(x4), float(z4)))


def extract_bases_side(right_support: CoordDict, right_horizontal: CoordDict):
    """
    婵犵數鍎戠徊钘壝归崒鐐茬獥婵°倕鎷嬮弫鍡樼節婵犲倻澧涢柛?V2闂傚倷鐒︾€笛呯矙閹烘鍤屽Δ锝呭幗閻戣棄绀冩い鏃囧亹椤︻噣姊虹紒姗堜緵闁哥姵甯″畷鎴﹀箻鐠囪尙鐤€濡炪倕绻愬ú銈夌嵁閳ь剟姊绘繝搴′簻婵炲眰鍊濆畷顖烆敃閿旂粯鏅銈嗘⒒閻℃棃鎮楅弻銉︾厵闂侇叏绠戦悘锝囩磼閻樺磭澧紒缁樼箖缁绘盯宕归鐟颁壕闁硅揪绠戦悞鍨亜閹哄秶顦﹂柣鎾亾缂傚倷娴囨ご鍝ユ崲閸儱钃熼柛娑欐綑閸欏﹪鐓崶銊︾缂佹柨銈稿?Front闂?
    """
    # 1. 闂傚倷绀侀崥瀣磿閹惰棄搴婇柤鑹扮堪娴滃綊鏌涢妷锝呭闁稿海鍠栭弻锟犲炊閵夈儳浠奸梺鍛婃煟閸庣敻寮诲☉銏犵厸濞达綀顫夐崕鎾绘⒑闂堚晝绉甸柛銊ョ埣楠?
    bottom = _bottom_from_support(right_support, axis="y")
    if bottom is None:
        return None
    (y7, z7), (y8, z8) = bottom
    
    bottom_center_y = (y7 + y8) / 2.0
    bottom_width = abs(y8 - y7)

    # 2. 闂傚倷娴囬妴鈧柛瀣崌閺屾盯顢曢敐鍡欘槰闂佽壈灏欐慨鎾€旈崘顔嘉ч柛娑卞弾閺嗐垽姊?
    candidates = []
    for seg in right_support.values():
        (py1, pz1), (py2, pz2) = seg
        top_pt = (py1, pz1) if pz1 < pz2 else (py2, pz2)
        candidates.append(top_pt)
            
    if not candidates:
        return None

    # 3. 闂傚倷绶氬褍螞濞嗘挸绀夐柡鍥ュ灩閻鎲搁弮鍫濊摕闁靛ň鏅╅弫濠勭磽娴ｅ顏勵嚕閸喒鏀芥い鏃傛櫕缁犳壆绱掗幓鎺濈吋闁糕斁鍋撳銈嗗笂缁€渚€鎮￠埀顒傜磽娴ｆ垝鍚褎顨呴…鍥ㄧ節濮橆剛鍊為梺闈涱煭缁犳垼顣介梻鍌欑窔濞艰崵绱為崱妯碱洸闁绘劕鎼壕?
    valid_tops = []
    threshold = (bottom_width / 2.0) * 2.5 
    
    for pt in candidates:
        dist = abs(pt[0] - bottom_center_y) # 闂備礁鎼ˇ顐﹀疾濠婂牊鍋￠柍鍝勬噹闂?pt[0] 闂?y
        if dist < threshold:
            valid_tops.append(pt)
            
    if len(valid_tops) < 2:
        valid_tops = candidates

    # 4. 闂傚倷绀佸﹢閬嶅磿閵堝洦鏆滈柟鐑樻婵櫕銇勯幘璺烘灁闁崇粯妫冮獮鏍庨鈧俊鐑芥煕鐎ｎ偅灏扮€垫澘瀚埀顒婄秵娴滆埖绂?
    valid_tops.sort(key=lambda p: (p[1], p[0]))
    
    if len(valid_tops) < 2:
        return None
        
    t1, t2 = valid_tops[0], valid_tops[1]
    
    if t1[0] > t2[0]:
        t1, t2 = t2, t1
        
    (y5, z5), (y6, z6) = t1, t2

    return ((float(y5), float(z5)), (float(y6), float(z6)),
            (float(y7), float(z7)), (float(y8), float(z8)))


def compute_heights_and_angles(front_bases, side_bases):
    """
    闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晛鈹戦悩宕囶暡闁?
    - z_topF = (z1+z2)/2, z_topS = (z5+z6)/2
    - h_front, h_side 闂傚倷鐒︾€笛呯矙閹达附鍋嬪┑鐘插閸嬫捇宕归銈囩厜閻?/闂?闂傚倷鐒﹂惇褰掑礉瀹€鈧埀顒佺殰閸パ呭姦濡炪倖甯婇懗鍫曟儗閸℃稒鐓犻柛顭戝亜閻忔挳鏌熼鐣屾噮婵炴垹鏁诲畷銊╊敍濠婂啯妲紓鍌氬€风粈渚€宕愭繝姘？闁汇垻顭堥悞鍨亜閹哄秷鍏岀紒鐘虫崌閺屾稑鈻庨幇顓狀槬濡炪倖娲╃紞鈧紒鐘崇洴婵＄柉顦存い?
    - 闂? 闂?闂傚倷鐒︾€笛呯矙閹达附鍋嬪┑鐘插閸嬫捇宕归銈囩厜閻?/闂?闂?cos 闂傚倷鑳堕…鍫澝瑰璺虹婵炲棙鍨堕～鏇㈡煥閻斿搫校闁哄拋鍓氱换娑㈠箣閻戝棛鍔烽梺鍝勵槷缁瑩寮婚敐鍜佺叆闁告洦鍋掑Λ鍡涙⒑?arccos+闂備浇宕甸崰宥咁渻閹烘梻鐭嗗ù锝呮贡閻濆爼鏌嶈閸撶喖寮?
    """
    (x1,z1),(x2,z2),(x3,z3),(x4,z4) = front_bases
    (y5,z5),(y6,z6),(y7,z7),(y8,z8) = side_bases

    # 婵犵绱曢崑鎴﹀磹閺囥垺鍋夐柣鎾冲瘨閻?z 濠德板€楁慨鐑藉磻濞戙垹鐤柛顭戝櫘閻?
    z_topF = (z1 + z2)/2.0
    z_topS = (z5 + z6)/2.0

    # 婵犲痉鏉库偓鏇㈠磹瑜版帗鏅梺璇叉唉椤绻涙繝鍥ф瀬鐎广儱顦柋鍥煏韫囧鐏柟顖ょ秮濮婃椽鎳栭埡鍌涙瘎婵犫拃鍕垫疁闁挎繄鍋ら、鏃堝炊閵夈倖鐫忔俊鐐€ら崑鎺楀窗濮樿京鐜绘俊銈傚亾闁宠棄顦甸獮妯肩驳鐟欏嫷鏆紓鍌欑劍椤ㄥ懘骞婅箛娑樼畾闁哄啫鐗嗛崡铏叏濡搫鏆辨鐐╁亾闂傚倷鑳剁划顖炲礉閺囩儑鑰块柛妤冨亹閺嬫棃鏌熺€涙濡囬柡瀣捣閹插憡鎯旈妸锕€鍓銈嗗笒閸婄懓鐣锋径瀣瘈闂傚牊绋撴晶閬嶆煟鎼淬垻鍙€闁?
    xm_top, zm_top   = (x1 + x2)/2.0, (z1 + z2)/2.0
    xm_bottom, zm_bottom = (x3 + x4)/2.0, (z3 + z4)/2.0
    h_front = math.hypot(xm_top - xm_bottom, zm_top - zm_bottom)

    ym_top, zm_top_s   = (y5 + y6)/2.0, (z5 + z6)/2.0
    ym_bottom, zm_bottom_s = (y7 + y8)/2.0, (z7 + z8)/2.0
    h_side = math.hypot(ym_top - ym_bottom, zm_top_s - zm_bottom_s)

    eps = 1e-9
    h_front = max(h_front, eps)
    h_side  = max(h_side, eps)

    # 闂備浇宕甸崰鎰版偡閿旂偓鏆滈柟鐑樻煛閸嬫挾鎲撮崟顐熸灆闂佽桨绀佺粔鐟扮暦婵傚憡鍋勫瀣閳诲骸鈹戦悙鑸靛涧缂佸弶瀵ч幈銊ョ暋閹佃櫕鐏侀梺纭呮彧缁犳垿鎮欐繝鍥ㄧ厵妞ゆ牕妫楅崯顐ゅ緤妤ｅ啯鍊垫繛鍫濈仢閺嬫稑螖閻樿尙绠虫俊?
    # 闂備胶鍘ч崯鍧楀疮閹绢喖鏋佺€广儱鎷嬪鈺呭级閸稑濡芥繛鍫涘灪缁绘盯骞樼€靛憡顔囬梺鎼炲劘閸斿秹濡撮崘鈺冪?婵犵數鍋為崹鍫曞箰閹间緡鏁勯柛娑卞灥婵娊鏌熼幆鏉啃撻柍閿嬪姍閺屾盯鈥﹂幋婵囩亪濡炪倖鏌ㄩ敃锕傚焵椤掑倹鍤€濠㈢懓锕畷鎶筋敍濠婂嫷娼熷┑锛勮檸濡?-y7| - |y6-y5|闂?/ (2 h_front)
    cos_theta = _clip( (abs(y8 - y7) - abs(y6 - y5)) / (2.0 * h_front) )
    theta = math.acos(cos_theta)

    # 闂備礁鎼悧婊勭椤忓牆鏋佺€广儱鎷嬪鈺呭级閸稑濡芥繛鍫涘灩閳规垿顢欓悾宀€顔囩紓鍌氱С缁€渚€鈥﹂崶顒佸亱闁割偀鎳囬弸?婵犵數鍋為崹鍫曞箰閹间緡鏁勯柛娑卞灥婵娊鏌熼幆鏉啃撻柍閿嬪姍閺屾盯鈥﹂幋婵囩亪濡炪倖鏌ㄩ敃锕傚焵椤掑倹鍤€濠㈢懓锕畷鎶筋敍濠婂嫷娼熷┑锛勮檸濡?-x4| - |x1-x2|闂?/ (2 h_side)
    cos_delta = _clip( (abs(x3 - x4) - abs(x1 - x2)) / (2.0 * h_side) )
    delta = math.acos(cos_delta)

    return (z_topF, z_topS, h_front, h_side, theta, delta)

def _norm_front_point(x: float, z: float, x4: float, z_topF: float) -> Tuple[float,float]:
    # 闂佽崵鍠愮划搴㈡櫠濡ゅ啯鏆滃┑鐘插閸楁岸鏌熺紒銏犳灈缂佲偓瀹€鍕厸鐎广儱娲﹂弳鈺冪磼閹邦収娼籣f'' = x - x4闂?z1'' = z - z_topF闂傚倷鐒︾€笛呯矙閹达附鍋嬮柛鈩冪☉缁犳牗绻濇繝鍌氼伀闁崇粯妫冮幃妤呮晲閸屾稒鐝楃紓浣插亾閻庯綆鍋呴崣蹇旂節閸偅灏电紒澶婂缁辨帗娼忛妸褏鐤勯悗瑙勬穿缂嶄礁顕ｆ禒瀣垫晣闁绘柨顨庡顖炴⒑閼姐倕校闁告梹顨婂畷鎶芥晜閻愵剦娼?
    xf2 = float(x) - float(x4)
    z1p = float(z) - float(z_topF)
    return xf2, z1p

def _norm_side_point(y: float, z: float, y7: float, z_topS: float) -> Tuple[float,float]:
    # 闂佽崵鍠愮划搴㈡櫠濡ゅ啯鏆滃┑鐘插閸楁岸鏌熺紒銏犳灈缂佲偓瀹€鍕厸鐎广儱娲﹂弳鈺冪磼閹邦厸鎷s'' = y - y7闂?z2'' = z - z_topS闂傚倷鐒︾€笛呯矙閹达附鍋嬮柛鈩冪☉缁犳牗绻濇繝鍌氼伀闁崇粯妫冮幃妤呮晲閸屾稒鐝楃紓浣插亾閻庯綆鍋呴崣蹇旂節閸偅灏电紒澶婂缁辨帗娼忛妸褏鐤勯悗瑙勬穿缂嶄礁顕ｆ禒瀣垫晣闁绘柨顨庡顖炴⒑閼姐倕校闁告梹顨婂畷鎶芥晜閻愵剦娼?
    ys2 = float(y) - float(y7)
    z2p = float(z) - float(z_topS)
    return ys2, z2p

def sort_bases(bases):

    bottom_left, bottom_right, top_a, top_b = bases

    # 闂傚倷绀侀幉锛勬暜閸ヮ剙纾归柡宥庡幖閽冪喖鏌涢妷锝呭Ω濞存粍绮撻弻娑㈩敃閿濆棛顦ラ梺鍛婃煟閸庢娊鍩€椤掆偓缂嶅﹤顭囬懡銈囦笉闁硅揪绲绘禍?
    if top_a[0] < top_b[0]:
        top_left = top_a
        top_right = top_b
    else:
        top_left = top_b
        top_right = top_a

    # 闂傚倷绀侀幉锛勬暜閸ヮ剙纾归柡宥庡幖閽冪喖鏌涢妷锝呭闁稿海鍠栭弻锟犲炊閵夈儳浠奸梺鍛婃煟閸庢娊鍩€椤掆偓缂嶅﹤顭囬懡銈囦笉闁硅揪绲绘禍?
    if bottom_left[0] > bottom_right[0]:
        bottom_left, bottom_right = bottom_right, bottom_left

    return bottom_left, bottom_right, top_left, top_right

def reconstruct3d_front(front_total: CoordDict,
                        front_support: CoordDict,
                        front_horizontal: CoordDict,
                        side_bases) -> Dict[str, List[Point3D]]:
    """
    婵犵數鍎戠徊钘壝归崒鐐茬獥婵°倕鎷嬮弫鍡樼節婵犲倻澧涢柛?V3闂傚倷鐒︾€笛呯矙閹烘鍤屽Δ锝呭暞閸嬪嫰鏌嶈閸撴瑩婀佸┑鐘诧工閸熶即宕欒ぐ鎺撶厾闁割煈鍋勯悘杈╃磼閻樺磭娲寸€规洘锕㈤、姗€濮€閻樿尙绋囬梻鍌欑劍閻綊宕濆畝鈧埀顒佸嚬閸樹粙骞堥妸鈺佺倞妞ゅ繐鍊峰Ч妤呮⒒娓氬洤澧紒澶嬫綑閳诲秹濮€閳垛晛浜鹃柣鎰嚀閳ь剚鐗楃粋宥嗙鐎ｎ亞鍔?
    婵犵數鍋為崹鍫曞箰閸濄儳鐭撻柟缁㈠枛閻ゎ噣鏌嶈閸撶喖骞冪憴鍕懝濠电姴瀚敍鐔兼⒑娴兼瑧鎮肩紒顕呭灠椤曘儵宕熼顐㈡倯闂佺硶鍓濋…鍥礆娴煎瓨鈷戞慨鐟版搐婵″ジ鎮楀鐓庡⒋闁糕斁鍋撳銈嗗笂缁€浣虹矆閸愨斂浜滄い鎰剁秵濞堟粓鏌℃担鍝バ㈤柣锝嗙箞瀹曟﹢鏁愰崨顒€顥氶梺璇茬箳閸嬬喖宕戦幘鍓佹噮闂傚倷鑳堕崕鐢稿疾濞戙垺鍋ら柕濞у嫭娈伴梺鍦檸閸犳牠宕橀埀顒勬煟閻斿摜鎳冮悗姘煎墰缁﹪鏁冮埀顒勫Υ閹烘埈娼╅柍褜鍓熷畷閬嶅煛閸屾粎楔闂傚倷鐒﹂幃鍫曞磿鏉堛劍娅犻柦妯侯槴閺嬫棃鏌熺€电袥闁稿鎸惧☉鐢稿川椤曞懏顥夐梺璇叉唉椤绻涙繝鍥ф瀬鐎广儱娲ｅ▽顏堟煟閿濆懏婀版い鏃€鍨甸埞鎴︻敊閻ｅ瞼顔囩紓鍌氱М閸嬫挸顪冮妶搴′簻妞ゆ垵顦悾鐑藉醇閺囩喎鈧攱銇勯幒鍡椾壕濡炪値鍋勯惉濂稿箟閹间礁绾ч柛顭戝枦閸╃偤姊?3D 缂傚倸鍊风粈渚€寮甸鈧—鍐寠婢光晜鐩畷绋课旀担绋垮闂備礁鎲″ú锕傚磻閸曨嚪鐑藉川椤曞懏顔旈梺缁樺姈濞兼瑩鍩㈤弴鐔虹闂傚倹娼欏畵鍡椻攽?
    """
    # 1. 闂傚倷绀侀崥瀣磿閹惰棄搴婇柤鑹扮堪娴滃綊鏌涢妷顔煎缂佲偓閸曨垱鐓熸俊顖氥仒閸氼偆绱掓径濠冨仴闁哄本鐩崺鈩冩媴鐟欏嫬鍓甸梻?
    fbases = extract_bases_front(front_support, front_horizontal)
    # 濠电姷鏁搁崑娑⑺囬銏犵鐎广儱顦粈鍫澝归悡搴ｆ憼闁哄拋鍓氶幈銊ノ熼搹鐧哥礊缂備胶濮寸紞濠傤潖濞差亜绠甸柟鐑樻尰閹烽亶姊洪幖鐐插缂侇喖绉剁划瀣箳濡ゅ﹥鏅為梺鍓茬厛閸犳帡寮歌箛娑欌拺婵炶尙绮繛鍥煕閺傛鍎戞俊鍙夊姍閹虫粓宕归鈩冨攭婵犵數鍋為崹鍫曟偡閿曞倹鈷旂€广儱顦伴悡?side_bases闂傚倷鐒︾€笛呯矙閹达附鍎斿┑鍌滎焾閻忚櫕淇婇婵嗗惞闁崇懓绉电换婵嬫濞戝崬鍓抽悷婊堝亰閸ㄥ爼鐛弽銊︾秶闁告挆鍛闂佽绻愬ù姘跺闯閿濆钃?
    if not fbases or not side_bases: 
        return {}
    
    (x1, z1), (x2, z2), (x3, z3), (x4, z4) = fbases
    (y5, z5), (y6, z6), (y7, z7), (y8, z8) = side_bases

    
    # 2. 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晠鎮归崶褎鈻曟繛闂村嵆閺屻劌鈹戦崱鈺傂у┑鈩冦仠閸旀垿骞冨畡鎵虫瀻闊洦妫忓Λ鐐测攽閻愯尙鎽犻柨鏇樺灲楠炲棝宕橀鑲╊槹濡炪倕绻愬ú銈夌嵁閳ь剟姊绘繝搴′簻婵炲眰鍊濆畷顖炲箮閼恒儳鍘?X 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻?
    # 婵犵數鍋犻幓顏嗙礊閳ь剚绻涙径瀣鐎殿噮鍋婃俊鍫曞幢濡搫濡抽梻浣告惈濞层垽宕硅ぐ鎺戠闁靛鍎Σ鍫ユ煙閸喖鏆欐鐐寸墱缁辨帡鎼归悷棰佸闂佺懓鍢查幊搴ㄢ€﹂妸鈺佺劦妞ゆ帒鍊圭€氬鏌ｉ弮鍌氬付閻庢艾顦甸弻宥堫檨闁告挻绋撻崚鎺戔枎閹惧磭顦ㄩ梻濠庡亽閸樿棄螣婵犲洦鈷戞慨鐟版搐婵″ジ鎮楀鐓庡妞ゆ洩缍侀、妤呭礋椤掆偓濞?
    Cx = (x3 + x4) / 2.0
    
    # 3. 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晝绱撴担璇＄劷闁荤喎婀遍幉鎼佸箣閿旇偐绋忛柣搴秵閸犳牠鎮欐繝鍥ㄧ厵妞ゆ牕妫楃€氼垶宕ラ锝囩闁瑰鍋炵亸顓犵磼婢跺灏︽鐐插暣楠炴﹢骞栭鐔烘毈婵犵妲呴崹浼村箹椤愶富鏁婂┑鐘叉处閻撶喖鏌曟繛鍨姎妞ゅ繈鍊濋弻宥堫檨闁告挻姘ㄩ崚鎺戭吋閸ャ劌搴婃繛杈剧秬椤宕曢悢鍏肩叆闁哄倸鐏濈敮銊╂煕鐎ｎ偅灏柍瑙勫灴楠炴﹢宕滄笟鍥ㄐ熼梻鍌欑閹诧繝銆冮崨鏉戠柈闁秆勩仠閳ь兛绀侀埢搴ㄥ箻鐠哄搫绲炬俊鐐€栭崝鎴﹀磹閺嶎厽鍋╅梺顒€绉甸悡鏇熶繆椤栨稒顫楀瑙勶耿閹鎲撮崟顐熸灆闂?
    # 婵犵數鍋為幐濠氭儍濠婂牆鐐婇柕濠忚礋閳ь剙鍟穱濠囨倷椤忓嫧鍋撻弴銏″亯濠靛倻顭堢壕鍧楁煙缂併垹鏋涚痪顓涘亾濠电姷鏁告慨鎾磻閸℃稑鐤?
    W_top_s = abs(y6 - y5) / 2.0
    # 婵犵數鍋為幐濠氭儍濠婂牆鐐婇柕濠忚礋閳ь剙鍟撮弻鐔兼偂鎼达絾鎲煎┑鐐跺皺閸犳牕鐣烽弴銏犵妞ゆ棁鍋愰、鍛節閻㈤潧孝闁稿妫濆畷?
    W_bot_s = abs(y8 - y7) / 2.0
    
    # # 婵犲痉鏉库偓鏇㈠磹瑜版帗鏅梺璇叉唉椤绻涙繝鍌滄殾闁挎繂顦壕鍏肩節闂堟稑鏆欏ù?(Z闂?
    # Z_top = z5  # 婵犵數鍋為幐濠氭儍濠婂牆鐐婇柕濠忚礋閳ь剙鍟穱濠囨倷椤忓嫧鍋撻弴銏″亯濠靛倻顭堢壕?Z
    # Z_bot = z7  # 婵犵數鍋為幐濠氭儍濠婂牆鐐婇柕濠忚礋閳ь剙鍟撮弻鐔兼偂鎼达絾鎲煎┑鐐跺皺閸犳牕鐣?Z
    # Height = Z_bot - Z_top
        # 濠碘槅鍋撶徊浠嬪疮椤栫偛姹?婵犵數鍎戠徊钘壝归崒鐐茬獥闁哄稁鍘旈崶顒€钃熼柕澶涢檮濞呮牕鈹戦鏂や緵闁告挻绋撶划濠氬箣濠垫劖瀵岄梺闈涚墕閻楁粓宕崫鍕ㄦ斀闁绘劕寮堕崰姗€鏌熼鑽ょ煓濠碘剝鎮傞弫鍌滄嫚閹绘崹妤呮⒒閸屾艾鈧悂鎮ч崟顖氬瀭濠靛倻顭堥崥瑙勭節婵犲倸鏋ら柛鐔锋嚇瀵爼宕煎顓熺彆闂?Z 闂備礁鎼ˇ顖炴偋閸℃鑰块梺顒€绉撮悿鐐亜閹板墎鐣辩紒鐙欏洦鐓忓鑸殿焽閸樻盯鏌涘锝呬壕缂傚倸鍊烽懗鑸垫叏閻㈡悶鈧啴宕卞☉娆忓墾濡炪倖姊婚弲顐︽偡瑜版帗鍊甸柨婵嗘噹椤ｅ磭鐥?
    Z_top = (z1 + z2) / 2.0
    Z_bot = (z3 + z4) / 2.0
    Height = Z_bot - Z_top
    
    out: Dict[str, List[Point3D]] = {}
    
    for gid, seg in front_total.items():
        pts: List[Point3D] = []
        for (x, z) in seg:
            # --- X 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾绱炴笟鈧鑽や沪缁涘鎮戦梺鍛婁緱閸ㄨ櫕寰?---
            # 闂傚倷鑳堕崕鐢稿疾濞戙垺鍋ら柕濞у嫭娈伴梺鍦檸閸犳宕曟惔锝囩＜閻庯綆鍋掗崕銉╂煕閵堝洤孝闂囧绻濇繝鍌氭殶闁告垵缍婇弻銈夊垂椤愩垻浼囩紓浣哄У閻╊垰鐣峰鈧、姗€濮€閻樿尙绋囬梻鍌欒兌椤牓顢栭崨顖涘床闁瑰搫绉堕弰?
            X = x - Cx
            
            # --- Y 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾绱炴笟鈧鑽や沪缁涘鎮戦梺鍛婁緱閸ㄨ櫕寰?(濠电姷鏁搁崕鎴犲緤閽樺鏆︽い鎺戝€甸崑? ---
            # 闂傚倷绀侀幖顐ょ矓閻戞枻缍栧璺猴功閺嗐倕霉閿濆拋娼熷ù婊冪秺閺岀喖骞嗚閺嗚鲸銇勯妶鍛殗闁哄矉缍侀獮鍥敆娴ｇ晫顢呮繝?Z 闂傚倷鑳堕…鍫ユ晝閿曞倸违閻庯綆鍓氶～鏇熺節闂堟稓澧㈡俊顐灦閺岀喓绮欑捄銊ュ摵闂佺顑嗛幑渚€藝瀹曞洦鍠愰柡澶婄仢閺嗭絿鈧娲橀崝娆撳箠濠靛鐒介柨鏇楀亾闁诡喕鑳剁槐鎾存媴閸濆嫅锝嗐亜閵娿儺妯€妞ゃ垺鑹鹃～婵嬵敇瑜庨悾璇测攽閳藉棗鐏犻柟纰卞亰椤㈡瑦绻濋崒妤侇潔闂佸湱鍋撻崜姘跺磿韫囨柣浜滈柕蹇ョ磿閹冲洭鏌ｉ幙鍐ㄥ⒋妞ゃ垺娲熸俊鍫曞幢濞嗘劖顔忓┑鐘垫暩閸庢垹寰婇挊澶屾殾妞ゆ帒鍊甸崑?
            if abs(Height) < 1e-4:
                # 闂傚倸鍊搁崐鎼佸疮椤愩埄鍤曢柛顐ｆ处閺佸棙绻涢幋娆忕仾闁抽攱妫冮弻鏇㈠醇濠靛棭浠圭紓浣靛妺閸楀啿顫忔繝姘耿婵鍘ч弲锝囩磽娴ｄ粙鍝洪柣鐔叉櫊楠炴牞銇愰幒鎾充患闁诲繒鍋犲Λ鍕€栨繝鐢靛仦閸ㄥ爼骞愰崫銉х煋闁圭虎鍠栨婵犵數濮村ú銈夋儗濡や降浜滈柡宥冨妿缁犳捇鏌涘Ο缁樺唉闁?
                current_depth = W_top_s
            else:
                ratio = (z - Z_top) / Height
                current_depth = W_top_s + ratio * (W_bot_s - W_top_s)
            
            # 濠电姵顔栭崰妤冩崲閹邦喚绀婂ù锝呭閻掍粙鏌熷▓鍨灍闁哥姴妫濋弻娑㈠焺閸愮偓鐣风紓浣稿€搁悧鎾诲蓟閿濆惟闁靛鍎烘禒楣冩⒑閸濆嫭顥犻柛鐘崇墵閻涱噣骞嬮敂缁樻櫔闂佺硶鍓濋悷褔藝椤曗偓濮婄粯绗熼崶褌绨奸梺鐓庣秺缁犳牠骞冮妷鈺侀唶闁哄洨鍋熼崫妤呮⒑閸涘﹥瀵欓柛娑卞枤閳ь剦鍙冨娲閳哄嫮顦伴梺鍛婃煥閻倿濡存担绯曟瀻闁规崘娉涜ぐ鍡楊渻閵堝棗濮傞柛濠冪墵閹箖鏌嗗鍡欏帗闂侀潧顧€婵″洭鎯屾繝鍌ょ唵鐟滃繑绻涢埀顒佷繆椤愩垹鏆ｅ┑顔瑰亾闂佹枼鏅涢崯浼村礄閿熺姵鈷?
            # 闂?3D 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾寰婇崸妤€绀岄柡宥庡亝婵ジ鎮楅崷顓炐㈡鐐╁亾闂傚倷鐒︾€笛呯矙閹达附鍎楀〒姘ｅ亾妞ゃ垺鐟╁鎾偄鐞涒剝鐏?-Y 闂傚倷绀侀幖顐﹀磹婵犳艾绠犻柟鎹愵嚙缁?(濠电姷鏁搁崕鎴犲緤閽樺鏆︽い鎺戝€甸崑鎾舵兜閸涱喚褰х紓浣割儏椤︿即濡堕敂鐐磯妞ゎ厽鍨舵晥)
            Y = -current_depth
            
            # --- Z 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻?---
            # 婵犵數鍎戠徊钘壝洪敂鐐床闁告劦浜栭崑鎾诲垂椤愶綆妫冮悗瑙勬磸閸ㄤ粙骞冮姀锛勯檮濠㈣泛顑囩粙?Z (闂傚倷绀侀幉锟犳嚌閹灐褰掓倻閼恒儱浠洪柣鐘叉穿椤ュ棛鎲撮崟顒€顎撻柣鐐寸▓閸撴繈鎮￠悩宕囩闁哄鍨甸幃鎴炴叏濡濡块柛鎺撳浮閹粌螣鐏忔牗鐏冮梻渚€鈧偛鑻晶鎾煟濞戝崬鏋涢柣锝囧厴瀹?
            Z = z
            # print("DEBUG front seg:", gid, seg)
            pts.append((X, Y, Z))
        out[f"F_{gid}"] = pts
    
    return out


def reconstruct3d_right(right_total: CoordDict,
                        right_support: CoordDict,
                        right_horizontal: CoordDict,
                        front_bases) -> Dict[str, List[Point3D]]:
    """
    婵犵數鍎戠徊钘壝归崒鐐茬獥婵°倕鎷嬮弫鍡樼節婵犲倻澧涢柛?V3闂傚倷鐒︾€笛呯矙閹烘鍤屽Δ锝呭暞閸嬪嫰鏌嶈閸撴瑩婀佸┑鐘诧工閸熶即宕欒ぐ鎺撶厾闁割煈鍋勯悘杈╃磼閻樺磭娲寸€规洘锕㈤、姗€濮€閻樿尙绋囬梻鍌欑劍閻綊宕濆畝鈧埀顒佸嚬閸樹粙骞堥妸鈺佺倞妞ゅ繐鍊峰Ч妤呮⒒娓氬洤澧紒澶嬫綑閳诲秹濮€閳垛晛浜鹃柣鎰嚀閳ь剚鐗楃粋宥嗙鐎ｎ亞鍔?
    闂傚倷绀侀幖顐ょ矓閻戞枻缍栧璺猴功閺嗐倕霉閿濆懎顥忔繛闂村嵆閺屻劌鈹戦崱娆忊拡濠电偛鍚嬬敮锟犲蓟濞戙垹唯闁靛鍎幐鍐ㄢ攽閻愯尙澧涢柛銊ョ秺閸┾偓妞ゆ帒鍋嗛弨鐗堜繆椤愩垹顏柍褜鍓濋～澶嬬箾婵犲洤鏋佺€广儱娲ｅ▽顏堟煟閿濆懏婀版い鏃€鍨剁换娑㈠箻鐎靛憡顔囬梺绯曟閺呮粎绱炴繝鍥ㄢ拺闁硅偐鍋涢崝銈夋煕鐎ｎ偅灏伴柟渚垮姂瀹曞爼顢旈崒娆愮潖闂備礁鎲￠〃鍫ュ磻濞戙垺鍋?3D 缂傚倸鍊风粈渚€寮甸鈧—鍐寠婢光晜鐩畷绋课旀担绋垮闂備礁鎲″ú锕傚磻閸曨厾鐭嗗ù锝堫嚃濞堜粙鏌ｉ幇顓熺稇闁崇粯娲樼换娑㈡⒒閺夋垵绁繝?
    """
    # 1. 闂傚倷绀侀崥瀣磿閹惰棄搴婇柤鑹扮堪娴滃綊鏌涢妷顔煎缂佲偓閸曨垱鐓熸俊顖氥仒閸氼偆绱掓径濠冨仴闁哄本鐩崺鈩冩媴鐟欏嫬鍓甸梻?
    sbases = extract_bases_side(right_support, right_horizontal)
    if not sbases or not front_bases: 
        return {}
    
    (x1, z1), (x2, z2), (x3, z3), (x4, z4) = front_bases
    (y5, z5), (y6, z6), (y7, z7), (y8, z8) = sbases


    # 2. 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晝绱撴担璇＄劷闁荤喎婀遍幉鎼佸棘濞嗗墽鍔烽梺瑙勵問閸犳宕伴崱娑欑厱闁斥晛鍠氬▓鏇犵磼閸屾氨澧﹂柡宀嬬秮婵℃悂濡烽妷顔昏繕闂備胶鍘ч悘姘跺垂閼测晝涓嶆繛鎴欏灩缁€鍐┿亜閹惧崬鐏╃憸?Y 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻?
    Cy = (y7 + y8) / 2.0
    
    # 3. 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晠鎮归崶褎鈻曟繛闂村嵆閺屻劌鈹戦崱娆忊拡濠电偛鍚嬬敮锟犲蓟濞戙垹唯闁挎洍鍋撻柛鏂诲€栫换婵嬪焵椤掑嫷鏁傞柛娑卞灙閺嬫牠鎮楅獮鍨姎闁瑰啿绻樺畷鎰板础閻愬秵妫冨畷鎺懨归姀鈺€绨介柍褜鍓濋～澶嬬箾婵犲洤绠氶柛鎰靛枛缁€瀣煏婵炲灝鐏╁ù婊呭亾缁绘繃绻濋崒姘亾闂佸摜鍠庣粔褰掔嵁閺嶃劍缍囬柟瑙勫姇閹懘姊?
    # 濠电姵顔栭崰妤冩崲閹邦喚绀婂ù锝呭閻掍粙鏌ｅΔ鈧悧鍕濠婂牊鐓曟い鎰剁稻缁€鈧梺鍛婃煟閸庣敻寮诲☉妯滄棃鍩€椤掑嫭鏅濋柕鍫濐樈閺?
    W_top_f = abs(x2 - x1) / 2.0
    # 濠电姵顔栭崰妤冩崲閹邦喚绀婂ù锝呭閻掍粙鏌ｅΔ鈧悧濠囧磿閻斿吋鐓涢柛銉ｅ劚閻忊晠鏌涢弬璇插姦闁哄本绋戣灃闁逞屽墴閺佸啴濡舵径妯绘櫓?
    W_bot_f = abs(x3 - x4) / 2.0
    
    # # 婵犲痉鏉库偓鏇㈠磹瑜版帗鏅梺璇叉唉椤绻涙繝鍌滄殾闁挎繂顦壕鍏肩節闂堟稑鏆欏ù?
    # Z_top = z1
    # Z_bot = z3
    # Height = Z_bot - Z_top
        # 濠碘槅鍋撶徊浠嬪疮椤栫偛姹?婵犵數鍎戠徊钘壝归崒鐐茬獥闁哄稁鍘旈崶顒€钃熼柕澶涢檮濞呮牕鈹戦鏂や緵闁告挻绋撶划濠氬箣濠垫劖瀵岄梺闈涚墕閻楁粓宕崫鍕ㄦ斀闁绘劕寮堕崰姗€鏌熼鑽ょ煓濠碘剝鎮傛俊鍫曞幢濡厧濞囬梻鍌氬€搁崐鎼佹偋閸曨垰鍨傚┑鍌滎焾閸氳绻濇繝鍌氭灓闁哥喎鎳樺鍫曞醇濮橆厽鐝曢梺?Z 闂備礁鎼ˇ顖炴偋閸℃鑰块梺顒€绉撮悿鐐亜閹板墎鐣辩紒鐙欏洦鐓忓鑸殿焽閸樻盯鏌涘锝呬壕缂傚倸鍊烽懗鑸垫叏閻㈡悶鈧啴宕卞☉娆忓墾濡炪倖姊婚弲顐︽偡瑜版帗鍊甸柨婵嗘噹椤ｅ磭鐥?
    Z_top = (z5 + z6) / 2.0
    Z_bot = (z7 + z8) / 2.0
    Height = Z_bot - Z_top
    
    out: Dict[str, List[Point3D]] = {}
    
    for gid, seg in right_total.items():
        pts: List[Point3D] = []
        for (y, z) in seg:
            # --- Y 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾绱炴笟鈧鑽や沪缁涘鎮戦梺鍛婁緱閸ㄨ櫕寰?---
            # 闂傚倷鑳堕崕鐢稿疾濠靛鈧箓宕奸妷顔芥櫔濡炪倖姊婚弲顐︺€呴弻銉ョ閻庢稒顭囩粻鏍ㄧ箾閸涱垰鈻堟慨濠傤煼瀹曞ジ顢曢敐鍥╃崲闂備胶鍘ч悘姘跺垂閼测晝涓嶆繛鎴欏灩缁€鍐┿亜閹惧崬鐏╃憸鐗堢懇濮婅櫣绮欏▎鎯у壈缂備胶绮敮濠勮姳?
            Y = y - Cy
            
            # --- X 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾绱炴笟鈧鑽や沪缁涘鎮戦梺鍛婁緱閸ㄨ櫕寰?(闂備浇顕уù鐑姐€佹繝鍋芥盯宕熼娑樹壕? ---
            # 闂傚倷绀侀幖顐ょ矓閻戞枻缍栧璺猴功閺嗐倕霉閿濆拋娼熷ù婊冪秺閺岀喖骞嗚閺嗚鲸銇勯妶鍛殗闁哄矉缍侀獮鍥敆娴ｇ晫顢呮繝?Z 闂傚倷鑳堕…鍫ユ晝閿曞倸违閻庯綆鍓氶～鏇熺節闂堟侗鍎忕紒鐘垫暬閺岀喖鎮滃Ο铏逛憾闂佺顑嗛幑鍥箠濠靛鐒介柨鏇楀亾闁诡喕鑳剁槐鎾存媴閸濆嫅锝嗐亜閵娿儺妯€妞ゃ垺鑹鹃～婵嬵敇瑜庨悾璇测攽閳藉棗鐏犻柟纰卞亰椤㈡瑦绻濋崒妤侇潔闂佸湱鍋撻崜姘跺磿韫囨柣浜滈柕蹇ョ磿閹冲洭鏌ｉ幙鍐ㄥ⒋妞ゃ垺娲熸俊鍫曞幢濞嗘劖顔忛梻浣筋嚙濞寸兘銆佹繝鍋芥盯宕熼娑樹壕閻熸瑥瀚埢鏇㈡煛娴ｅ摜效鐎规洜鍘ч埞鎴﹀幢濡皷鍋撻锔界厽閹兼番鍊ゅ鎰版煟椤撗冩灓闁兼椽浜堕崺鍕礃椤忓棙鍤岄柣鐔哥矋閺屻劑鈥﹂崶銊ヮ嚤閻庢稒锚閸?X 婵犵數鍋犻幓顏嗗緤閻ｅ瞼鐭撻柛顐ｆ礃閸嬵亪鏌涢埄鍐姇闁?
            if abs(Height) < 1e-4:
                current_width = W_top_f
            else:
                ratio = (z - Z_top) / Height
                current_width = W_top_f + ratio * (W_bot_f - W_top_f)
            
            # 婵犵數鍋為幐濠氭儍濠婂牆鐐婇柕濠忚礋閳ь剙鍟撮弻锝夋偄閸濄儲鍣у┑鈽嗗亝椤ㄥ懘婀佸┑顔姐仜閸嬫捇鏌熼姘殻鐎规洜鍠栭、妤佹媴鐠団€虫櫃闂傚倷鑳堕、濠囶敋閺嶎厼闂い鏍ㄧ矋椤洘绻濋棃娑卞剰缂備讲鏅犻弻娑㈠箻濡も偓閹冲繘鎮楅銏♀拺闂傚牃鏅炵粈瀣煕閺傝法鐒搁柕鍡曠閳诲酣骞樼捄鍝勭稻婵＄偑鍊栭崝鎴﹀磹閺嶎厽鍋╅梺顒€绉甸悡鍐煏婢舵稑顩柣顓烇功閹叉悂鎮ч崼鐔封偓鎰繆椤愩垹鏆ｅ┑顔瑰亾闂佹枼鏅涢崯浼村礄閿熺姵鈷?
            # 闂?3D 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾寰婇崸妤€绀岄柡宥庡亝婵ジ鎮楅崷顓炐㈡鐐╁亾闂傚倷鐒︾€笛呯矙閹达附鍎楀〒姘ｅ亾妞ゃ垺鐟╁鎾偄鐞涒剝鐏?+X 闂傚倷绀侀幖顐﹀磹婵犳艾绠犻柟鎹愵嚙缁?
            X = current_width
            
            # --- Z 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻?---
            Z = z

            # print("DEBUG right seg:", gid, seg)
            
            pts.append((X, Y, Z))
        out[f"R_{gid}"] = pts
    return out






# ====== Splicing (闂?splicing.py) ======
# splicing.py - 濠电姷顣藉Σ鍛村垂椤忓牆鐒垫い鎺嗗亾缁剧虎鍙冮崺鈧い鎺戝€搁崢瀛橆殽閻愯尙绠荤€规洘顨婇幃鈩冩償閳藉棙些闂傚倷绀侀幉鈥愁潖婵犳艾绐楅柡鍥ュ灩缁€鍌涗繆椤栨瑧绉块柣鏃傚帶閻忔娊鏌ц箛锝呬簻濞?(闂佽姘﹂～澶愭偤閺囩儐鍤曢柟鎹愵嚙缁犵偤鏌曟繛鍨姶婵為棿鍗抽弻銊モ攽閸℃浼傜紓浣插亾閻庯綆鍠楅悡鏇㈡煃閸濆嫬顏柕鍡楀暟缁辨帡鈥﹂幋婵嗩潾缂備緡鍠掗弲鐘汇€佸☉姗嗙叆闁告剬鍐嚙闂傚倷鐒﹂惇褰掑礉瀹€鈧埀顒佸嚬閸犳岸鎳炴潏鈺傚磯闁靛绠戦崢鐟邦渻閵堝棙鈷掗柍宄扮墦瀹曠敻鎮╁顔藉仴?
import math
import numpy as np
from typing import Dict, List, Tuple, Set

# 缂傚倸鍊风欢锟犲磻婢舵劦鏁嬬憸鏃堝箖濡ゅ懏鍊婚柦妯侯槺椤︻偄顪冮妶鍡楀闁搞劍妞藉畷鎰暦閸ワ絽浜鹃柣鐔哄閸熺偟鎲搁弶鍨殭闁挎洏鍨介、鏃堝醇濠靛浂妫熼梻浣规偠閸庡姊介崟顖ｆ晝闁伙絽澶囬崑鎾斥枔閸喗鐏€闂佺顑嗛幐鎼佲€﹂崸妤佸殝闁割煈鍋嗙粙鍥⒑娴兼瑧鎮奸柛瀣尵缁?
AllModelsData: TypeAlias = Dict[str, Dict[str, Any]]


def _find_splicing_points(f3d: Model3DData, support_keys: Set[str], mode: str) -> List[Point3D]:
    """
    闂傚倷绶氬鑽ゆ嫻閻旂厧绀夌€广儱鐗嗛弳鐐烘⒒娴ｈ鍋犻柛鏂跨焸椤㈡牠宕卞☉杈ㄦ櫌濠电姴锕ら幊蹇涘窗閸℃稒鐓曢柍鈺佸枤濞堟洜绱掗崒姘卞ⅵ闁哄矉缍佹俊鎼佸Ψ閵夘喕杩樼紓鍌欑劍閵囩偤鎳楅崜浣诡潟闁圭儤鏌￠崑鎾斥槈濞呰櫕鍨甸埢鎾诲醇閺囩喓鍘甸柣鐘叉礌閳ь剝娅曢悘鍡涙⒑閻撳海浠涢柛銊ユ健瀵偄顓奸崶锔藉媰闂佽鍨庣仦缁㈡（闂傚倷绀侀幉锛勬暜閻愬瓨娅犳俊銈呮噹閺嬩焦銇勯弴妤€浜惧Δ鐘靛仦閿曘垽鐛€ｎ喗鍊烽悗闈涙憸灏忔繝鐢靛仜椤曨厽鎱ㄦィ鍐ㄦ槬闁哄诞浣插亾閹烘鍤嬮柣銏㈩暯閺?闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鐐灱濡插牓鏌熼悙顒€澧柛搴㈠灦缁绘盯宕奸悢椋庝紝闂佸搫鑻ú顓㈠极閹版澘绀嬫い鎾楀倻绀冮梻浣筋嚙缁绘帡宕戝☉銏犵９闁绘垼濮ら崵鍫ユ煙鏉堥箖妾柛搴＄Ч閺屾盯寮撮妸銉ょ暗缂備胶濯崹鍫曞蓟濞戞ǚ鏋庨煫鍥ㄦ尭缁楊參鏌ｉ悙缈犱孩濡炴潙鎽滅划娆愬緞閹板灚鏅滈梺绯曟閺呮瑧妲愰幘缁樷拺缂備焦锚婵洨绱掗悩鑼ч柛鈹惧亾?
    - f3d: 濠电姵顔栭崰妤冩崲閹邦喚绀婇柍褜鍓氶妵鍕敃閵忊晛鍓堕悗瑙勬礀閻栫厧鐣峰鍡╂Ъ闂佷紮绲藉畷顒勫煡婢舵劕绠婚柟棰佺劍妤旀繝鐢靛剳缂嶅棝宕抽敐鍜佸殨妞ゆ劧闄勯崑瀣煕椤愶絿绠橀柕鍫畵閺岋絾鎯旈姀鈶╁濡炪們鍔岄幊妯虹暦閵夆晛鐒?
    - support_keys: 濠电姵顔栭崰妤冩崲閹邦喚绀婇柍褜鍓氶妵鍕敃閵忊晛鍓堕悗瑙勬礀閻栫厧鐣烽敐澶娢ㄩ柕濞垮劚缁犳垿姊绘担鍛婂暈缂佽绉电粋宥呪枎閹达絽小缂備讲鍓濇晶顒勬⒒娴ｅ憡鎯堥悗姘卞厴瀹曞綊鏌嗗鍛€銈嗘磵閸嬫挻顨ラ悙杈捐€挎鐐差儔閹瑧鈧潧鎽滃皬婵?
    - mode: 'top' 闂?'bottom'
    
    闂傚倷鑳堕…鍫㈡崲閹寸偟绠惧┑鐘叉搐閺嬩焦銇勯幘璺烘灁闁崇懓绉甸妵鍕籍閸屾瀚涘┑鈩冨絻椤兘寮?
    1. 闂傚倷娴囬妴鈧柛瀣崌閺屾盯顢曢敐鍡欘槰闂佽壈灏欐繛鈧柡宀€鍠撻崰濠偽熸潪鏉款棜闂傚倷绀侀幖顐︽偋閸℃蛋鍥ㄥ閺夋垶鐎銈嗘磵閸嬫挻顨ラ悙杈捐€挎鐐差儔閹瑧鈧潧鎽滃皬婵犵數鍋涢顓熸叏鐎涙ɑ娅犻幖鎼厛閺佸倹銇勯幒鎴濐仾闁?
    2. 闂傚倷绀佸﹢閬嶁€﹂崼銉ｂ偓渚€濡舵径瀣幈閻熸粌閰ｅ畷婵嬪冀椤撶喎浜梺鎸庣箓椤︻垳绮婚幎鑺ョ厵闁绘垶锚閻忊晝鐥弶璺ㄐч柡灞诲妼閳藉螣缂佹ɑ瀚冲┑鐘灱椤鏁冮姀鐘垫殾婵鍩栭崑瀣煕椤愩倕鏋嶇紒顕呭灡缁?闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鐐灱濡插牓鏌熼悙顒€澧柛搴㈠灦缁绘盯宕奸悢椋庝紝闂佸搫鑻ú顓㈠极閹版澘绀嬫い鎾楀倻绀冮梻浣筋嚙缁绘帡宕戝☉銏犵；濠电姴瀚～鏇熸叏濡や焦銇濋柡灞剧⊕缁绘繈宕ㄩ婵囩潖婵犵數鍋炲娆撍囬弶娆剧劷濠电姵鑹剧粻锝夋煟濡櫣锛嶉柡鍡欏█濮婅櫣绱掑Ο鍝勵潕濠电偛鎳岄崹璇参?
    3. 闂傚倷绶氬鑽ゆ嫻閻旂厧绀夐煫鍥ㄤ緱閺佸鎱ㄥΟ鍝勭秮婵炲矈浜弻娑氫沪閸撗勫櫙闂佸憡锕╅崜鐔煎蓟閻旂厧鍨傛い鎰╁灩婵垽姊虹化鏇熸珔闁兼椿鍨堕、娆掔疀濞戞瑦娅囬梺閫炲苯澧查柕鍥ㄥ姍瀹曘劍绻濋崟銊︾亙闂備線娼ч悧鍡欌偓姘嵆瀹曠數鈧綆鍠楅悡娑㈡煕椤愶綀澹樺ù婊呭亾缁绘繈濮€閿濆懐鍘梺缁橆殕濡啫顕ｉ弻銉ラ唶闁哄洨鍠庨崜顓㈡⒑閸涘﹥澶勯柛妯哄悑缁傛帡顢涢悙瀵稿弳濠电偞鍨惰摫閻犳劦鍙冨铏圭矓閸℃顏╁┑顔肩墦閺岋綁寮介悽鐢敌滈悗娈垮枤閺佸宕洪埀顒併亜閹烘垵鈧兘鎮炴繝鍥╁彄闁搞儯鍔嶇亸浼存倵濮橆厾鍙€闁哄矉绻濆畷鐓庮潩椤戝灝顥氭繝鐢靛О閸ㄥ綊鎮ラ姀鐙€鍚嬮柛銉㈡櫓濡?
    4. 闂備礁鎼ˇ顐﹀疾濠婂牆钃熼柕濞垮剭濞差亜鍐€闁靛缂氬锕€鈹戦悙鍙夘棞婵﹫绠撻崺娑㈠醇濠靛啯顫嶉梺鐟扮仢閸熲晝鑺辨禒瀣厱閻庯絽澧庣粙濠氭煙瀹勭増鍣规い顓滃姂閸┾偓妞ゆ帒鍊圭€氬鏌ｉ弬鎸庡暈濞存嚎鍊濋弻锝夊箛椤撶喓绋囨繝銏ｆ硾缁夊綊寮?
    """
    support_endpoints = []
    for gid, seg in f3d.items():
        original_id = gid.replace("F_", "")
        if original_id in support_keys:
            support_endpoints.extend(seg)

    if not support_endpoints:
        raise ValueError("support endpoints are unavailable")

    # 闂傚倷绀佸﹢閬嶁€﹂崼銉ｂ偓渚€濡舵径瀣幈閻熸粌閰ｅ畷婵嬪冀椤撶喎浜梺鎸庣箓椤︻垳绮婚幎鑺ョ厵闁绘垶锚閻忊晝鐥?
    reverse_sort = (mode == 'bottom')
    support_endpoints.sort(key=lambda p: p[2], reverse=reverse_sort)

    if len(support_endpoints) < 2:
        raise ValueError("not enough support endpoints for splicing")

    # 闂傚倷鑳堕幊鎾绘倶濮樿泛纾块柟鎯版閺勩儳鈧厜鍋撻柛鏇ㄥ亜閻濇﹢姊洪柅鐐茶嫰婢ь垳绱?闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鐐灱濡插牓鏌熼悙顒€澧柛搴㈠灦缁绘盯宕奸悢椋庝紝闂佸搫鑻ú顓㈠极閹版澘绀嬫い鎾楀倻绀冮梻浣筋嚙缁绘帡宕戝☉銏犵；濠电姴瀚～鏇熸叏濡や焦銇濋柡灞剧⊕缁绘繈宕ㄩ婵囩潖婵犵數鍋炲娆撍囬弶娆剧劷濠电姵鑹剧粻锝夋煟濡櫣锛嶉柡鍡欏█濮婅櫣绱掑Ο鍝勵潕濠电偛鎳岄崹璇参?
    z_ref = support_endpoints[0][2]
    z_tolerance = 1.0  # Z闂傚倷鑳堕…鍫ユ晝閿曞倸鍌ㄧ憸宥夋晝?mm婵犵數鍋涢顓熸叏娴兼潙纾块梺顒€绉撮懜褰掓倵闂堟稒鍟炲┑顖氥偢閺屾洟宕煎┑鍡╀紓缂備讲鍋撻悗锝庡枟閻撴盯鏌涢弴銏℃锭闁诲繒濞€閺岀喖顢欓懞銉ラ瀺缂備礁顑呴ˇ鐢稿春閳ь剚銇勯幒鎴濃偓宄扳柦?
    
    same_z_layer = [p for p in support_endpoints if abs(p[2] - z_ref) < z_tolerance]
    
    if len(same_z_layer) < 2:
        # 婵犵數濮烽。浠嬪焵椤掆偓閸熷潡鍩€椤掆偓缂嶅﹪骞冨Ο璇茬窞闁归偊鍓濊闂佽绻掗崑鐘诲磻閹伴偊鏁傞梺顒€绉甸崐鍫曟煟閹邦厼绲婚柍褜鍓欓…宄扮暦閹达附鏅插璺猴攻閻庮剚淇婇锔绘殥闁煎啿鐖奸幃宄扳攽鐎ｎ偄浠?婵犵數鍋為崹鍫曞箹閳哄倻顩插瀣椤洘绻濋棃娑氬闁绘帒锕鍫曞醇濮橆厽鐝曢梺鍝勬缁绘﹢寮婚敓鐘查唶婵﹩鍏涙竟鏇炩攽?闂傚倷绀侀幖顐︽偋閸愵喖纾婚柟鐐灱濡插牓鏌熼悙顒€澧柛搴㈠灦缁绘盯宕奸悢椋庝桓缂備礁顑呴ˇ鍨繆閸洖绀嬫い鏍ㄧ閻ゅ倿姊?
        same_z_layer = support_endpoints[:2]
    
    # 闂傚倷绶氬鑽ゆ嫻閻旂厧绀夐煫鍥ㄤ緱閺佸鎱ㄥΟ鍝勭秮婵炲矈浜弻娑氫沪閸撗勫櫙闂佸憡锕╅崜鐔煎蓟閻旇櫣鐭欐繛鍡欏亾閺呬粙姊绘担渚綊闁告洦鍋勯～宥夋⒑缂佹澹勭紓宥勭窔閻涱噣骞掑Δ鈧粻鎶芥煙鐎电啸妞わ絾鐓″娲箰鎼达絺妲堥梺鍝勭墱閸撴氨绮╅悢濂夋建闁逞屽墮閻ｅ嘲顫濈捄铏归獓婵犮垼娉涢幗婊堫敊閸℃稒鈷戦柛娑橈功閹冲啴鏌涘Ο鑽ゅ⒈闁诡噮鍠楀蹇涘Ω瑜夐弸鏍ь渻閵堝懐绠伴柟鍐茬箲缁傛帒螣娓氼垳鍞甸梺鐓庢憸閺佸憡鏅惰閺岋繝宕ㄩ鐘茬厽闂佽鍨伴崯鏉戠暦閻旂⒈鏁囬柣鎰緲鐎?
    same_z_layer.sort(key=lambda p: p[0])
    
    # 闂備礁鎼ˇ顐﹀疾濠婂牆钃熼柕濞垮剭濞差亜鍐€鐟滄粓宕崨瀛樼叆闁哄洦顨呮禍楣冩偡濠婂嫭绶查柟璇х磿缁瑦寰勯幇顑┭囨煕閺囥劌鐏犳繛鍫熺箞濮婃椽宕崟顓烆暤闂佺顑嗛幐鎼佲€﹂崸妤佸殝闁汇垽娼ч埅鍫曟⒑閸濆嫭鍣归柣鏍с偢楠炲棝宕橀鑲╊槹濡炪倖鎸鹃崑姗€宕?
    left_point = same_z_layer[0]
    right_point = same_z_layer[-1]
    
    print(f"  - 闂傚倷鑳堕幊鎾诲床閺屻儱瑙﹂悗锝庡墯閺嗘粓鏌熺紒銏犳灍闁?({mode}): 闂?{left_point}, 闂?{right_point}")
    
    return [left_point, right_point]


def get_rotation_matrix(v1, v2):
    """ 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晝绱撴担璇＄劷妞も晝鍏橀獮鏍垝閻熸澘鈷夐梺绋匡工椤嘲顫忓ú顏勭闁圭儤鏌х憰?闂傚倷绀侀幉锛勬暜閻愭祴鏋?闂傚倷鐒﹂惇褰掑礉瀹€鈧埀顒佸嚬閸樿壈鐏嬮梺绯曞墲钃卞┑顔界矋閵囧嫰骞掗幋婵冨亾婵犳艾鐭楅柟鎵閳锋帡鏌涢幇鍏哥暗濞存粍鐗犲娲箰鎼达絺妲堟繝闈涘€瑰鍦崲濞戙垹鐐婄憸婊堝吹?R*v1 婵?v2 濠德板€楁慨鐑藉磻濞戙垺鍋柛銉厵閳?"""
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)

    # 婵犵數濮烽。浠嬪焵椤掆偓閸熷潡鍩€椤掆偓缂嶅﹪骞冨Ο璇茬窞闁归偊鍓濊闂備胶顢婇幓顏嗙不閹存績鏋嶉柕鍫濇礌閸嬫挾鎲撮崟顓熸啓闁诲繐绻戦悷褔宕氶幒妤佹櫢闁绘﹢娼х粊锕傛煟鎼粹剝璐″┑顖ｅ弮瀵劍绂掔€ｎ偆鍘甸柣搴㈢⊕椤洦鏅堕鍡忓亾濞堝灝鏋欑紒顔界懃閻ｇ兘濡烽埡浣侯吅濠电娀娼ч鍡欎焊濞嗘挻鐓熼柣鎰嚟閳藉鏌ｉ鐑嗘Ш婵″弶鍔曢埞鎴犫偓锝庝簽椤︻偄鈹戦悙鍙夘棡闁告梹鐗犻弫鎾诲Ψ閳哄倵鎷婚梺鎼炲劵缁茶姤绂嶆ィ鍐┾拺闁告繂瀚弳娆愩亜閹存繄澧曢棁澶愭煕閳╁啰鈽夌紒鐙呯秮閺屸€愁吋閸愩劌顬夊銈冨劚椤戝顕?80闂?
    if np.allclose(v1, v2):
        return np.identity(3)
    if np.allclose(v1, -v2):
        return -np.identity(3)

    # 婵犵數鍋犻幓顏嗙礊閳ь剚绻涙径瀣鐎殿噮鍋婃俊鑸靛緞婵犲憛鏇㈡⒑绾懏褰х紒鐘冲灥閳诲秹濡舵径瀣幈濠电偛妫楀ù姘ｆ搴ｇ＜闁绘ê鎼崥褰掓煙瀹勯偊鍎旈柡浣哥Ч瀹曠喖顢橀悢鍝ユ闂傚倷绀侀幖顐﹀疮椤愶富鏁勯柛顐ｇ贩瑜版帒骞㈡俊顖濐嚙椤繝姊洪崫鍕垫Ч闁搞劌澧庨埀顒佺閻擄繝骞冨畡鎵虫瀻闁归偊鍓涢悷銊╂煟?
    cross_prod = np.cross(v1, v2)
    dot_prod = np.dot(v1, v2)

    s = np.linalg.norm(cross_prod)
    c = dot_prod

    vx = np.array([
        [0, -cross_prod[2], cross_prod[1]],
        [cross_prod[2], 0, -cross_prod[0]],
        [-cross_prod[1], cross_prod[0], 0]
    ])

    # 缂傚倸鍊搁崐鎼佸疮椤栫偑鈧啴宕ㄧ€涙ê鍓︽繝銏ｅ煐閸旀牠鎮￠崒鐐村€堕柣鎰絻閳锋柨顭跨憴鍕闁哄矉绻濆畷姗€鈥﹂幋婵嗗婵犵數鍋炲娆徫涘┑鍡欐殾婵°倕鎷嬮弫鍡涙煃瑜滈崜娑樜?
    rotation_matrix = np.identity(3) + vx + vx.dot(vx) * ((1 - c) / (s ** 2))
    return rotation_matrix


def _align_and_transform_model(model_data: Dict[str, Model3DData],
                               source_p1: Point3D, source_p2: Point3D,
                               target_p1: Point3D, target_p2: Point3D):
    """
    闂備浇顕х花鑲╁緤婵犳熬缍栧璺洪閺嗙偤姊绘担瑙勫仩闁告柨鐭傞、鏍醇閵忊€冲簥濠碘槅鍨伴崥瀣磻濮椻偓閹﹢鎮欓崹顐ｇ彧闂佸搫妫欏畝鎼佸蓟閳╁啯濯撮柛鎾村絻濞堣泛鈹戦悙鑼闁搞劌鐏濋悾宄邦潩椤掑鍍靛銈嗗姂閸婃鐡忛梻鍌欑閹诧繝鎮烽敃浣规噷闁诲氦顫夊ú姗€鎮￠敓鐘叉瀬鐎广儱顦柋鍥ㄧ節闂堟侗鍎愰悘蹇旂懅缁辨挻鎷呴崜鍙壭ч梺娲讳簻缂嶅﹪宕洪埀顒併亜閹达絽鍔甸柛蹇撶灱缁辨捇宕掑鍏尖枅閻庢鍠撻崝宥囩矚闁秴绠ュù锝夋櫜婢规洘绻涙潏鍓хК妞ゎ偄顦佃棢閻庯綆鍠栫痪褔鏌ｉ幋婵囶棞濠⒀冨⒔缁辨帗娼忛妸銉ユ懙闂?
    婵犵數鍋犻幓顏嗗緤娴犲鍊舵繝闈涚墛椤愪粙鏌涘Δ鍐ㄤ汗闁衡偓閿曞倹鐓欓梺顓ㄧ畱閺嬫稑霉閻欌偓閸ㄥ爼骞?source_p1, source_p2)缂傚倸鍊风欢锟犲窗閺嶃劍娅犲ù鐘差儏閻忚櫕鎱ㄥ璇蹭壕閻庢鍠曢崡鎶藉箖閳哄懏鍤戞い鎺嶇贰閸熷懘姊绘担鍛婂暈閻㈩垱顨嗙粩鐔煎幢濡炴洜鍎ょ€靛ジ寮堕幋婵嗘暏闂備焦鎮堕崕顕€寮插☉娆戭浄妞ゆ牜鍋為崐?target_p1, target_p2)闂?
    """
    # 闂備浇顕х换鎰崲閹邦儵娑橆煥閸涱噮鍋ㄥ銈嗘尪閸ㄥ湱绮堥崒鐐寸厪濠㈣鍨伴崯鈺呭礌閺嶎厽鐓涘璺鸿嫰閸撻亶鏌涢幘纾嬪闁伙絿鍏樺畷锝嗗緞鐏炲憡鐏冪紓鍌欓檷閸斿本鏅跺鐎檡闂傚倷娴囧銊╂倿閿旂晫鐝堕柛鈩冪懃閸?
    A1 = np.array(source_p1)
    A2 = np.array(source_p2)
    B1 = np.array(target_p1)
    B2 = np.array(target_p2)

    # 1. 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晠鏌ゆ慨鎰偓妤冨娴犲鐓冮柛婵嗗閳ь剙缍婂鎯般亹閹烘挾鍘遍梺闈涳紡閸愬啨鍨介弻?
    dist_A = np.linalg.norm(A2 - A1)
    dist_B = np.linalg.norm(B2 - B1)
    if dist_A < 1e-9:
        raise ValueError("source connection points are too close")
    scale = dist_B / dist_A
    print(f"  - 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晠鏌ゆ慨鎰偓妤冨娴犲鐓冮柛婵嗗閳ь剙缍婂鎯般亹閹烘挾鍘遍梺闈涳紡閸愬啨鍨介弻? {scale:.4f}")

    # 2. 闂備浇宕垫慨宕囨閵堝洦顫曢柡鍥ュ灪閸嬧晛鈹戦悩瀹犲缂侇偄绉归幃妤呮晲鎼粹€崇缂備椒绶￠崳锝夊蓟閿濆鏁囨繛鎴炵懄閻濇艾鈹戦埥鍡楃仚闁?
    vec_A = A2 - A1
    vec_B = B2 - B1
    rotation_matrix = get_rotation_matrix(vec_A, vec_B)
    print("  - transform step completed")

    # 3. 闂備浇顕х花鑲╁緤婵犳熬缍栧璺洪閺嗙偤姊绘担瑙勫仩闁告柨鐭傞、鏍礋椤栨稑娈橀梺鐟扮摠缁娊骞掗弴鐘垫澑闁瑰吋鐣崝灞解枔濠靛鈷戠紓浣姑慨澶愭煙閾忣偅灏甸柤娲憾瀵濡烽敃鈧禒娲⒑闂堟侗鐒鹃柛搴や含缁辩偞绗熼埀顒勫蓟?
    for view_data in model_data.values():  # 闂傚倸鍊风欢锟犲礈濞嗘垹鐭撻柡澶嬪焾閸?f3d 闂?r3d
        for gid in view_data:
            transformed_seg = []
            for p_tuple in view_data[gid]:
                P = np.array(p_tuple)
                # a. 闂傚倷鑳堕崕鐢稿疾濠靛鈧箓宕奸妷顔芥櫔濡炪倖娲嶉崑鎾垛偓? 闂備浇顕х换鎰崲閹邦儵娑樷槈閵忕姷锛涘銈冨€栭悧妤呫€冮妷鈺傚€烽柤纰卞墾缁辩偛霉濠婂嫮娲撮柡灞剧洴楠炴帒螖婵犲啯顓煎┑鐐茬摠缁秵鏅?婵犵數鍋為崹鍫曞箰閹间礁绠规い鎰╁€栭弳婊勩亜閹板爼妾柛濠勫厴閺屾盯鏁傜拠鎻掔闂佷紮缍佹禍鍫曞蓟濞戞粠妲奸梺鍛婃⒐閻楃娀骞冮妷鈺傛櫜闁搞儜鍐惧殭?
                P_relative = P - A1
                # b. 缂傚倸鍊搁崐鎼佸磹閻㈢鐤炬繝濠傜墕濡?
                P_scaled = P_relative * scale
                # c. 闂傚倷绀侀幖顐﹀疮椤愶富鏁勯柛顐ｇ贩?
                P_rotated = rotation_matrix.dot(P_scaled)
                # d. 缂傚倸鍊搁崐鐑芥倿閿旂偓宕查柛宀€鍎愰弫瀣亜閺囨浜鹃悗? 濠德板€楁慨鐑藉磻濞戞艾顥氭い鎾寸箘閺勫倿姊绘担鍛婂暈閻㈩垽绻濋妴鍌炴晜閻ｅ矈娲搁梺?婵犵數鍋為崹鍫曞箰閹间礁绠规い鎰╁€栭弳婊勩亜閹板爼妾柛濠勫厴閺屾盯鏁傜拠鎻掔闂佷紮缍佹禍鍫曞蓟閿濆鐓涘┑鐘插€归悘宥夋⒑缂佹澹勭紓宥勭閻ｇ兘骞栨担鍝ョ杸濡炪倖鎸炬慨鎾倶鏉堚晝纾?
                P_new = P_rotated + B1
                transformed_seg.append(tuple(P_new))
            view_data[gid] = transformed_seg
    print("  - transform step completed")


def splice_models(
    all_models_data: AllModelsData,
    auto_base_index: Optional[int] = None,
) -> Tuple[Model3DData, Model3DData]:
    """
    Splice all tower-body models into one shared 3D coordinate space.
    """
    # Keep this order consistent with dual_view_processor's input order.  A
    # plain string sort would place "10" before "9" and reverse their stack.
    model_names = sorted(all_models_data.keys(), key=_model_sort_key)
    print("\n" + "=" * 50)
    print("Model splicing")
    print("=" * 50)
    for i, name in enumerate(model_names):
        print(f"  {i + 1}: {name}")

    base_model_idx = -1
    if auto_base_index is not None and 0 <= auto_base_index < len(model_names):
        base_model_idx = auto_base_index
        print(f"Auto base model index: {auto_base_index + 1}")

    while base_model_idx < 0 or base_model_idx >= len(model_names):
        try:
            choice = input(f"Select base model (1-{len(model_names)}): ")
            idx = int(choice) - 1
            if 0 <= idx < len(model_names):
                base_model_idx = idx
            else:
                print("Invalid index, try again.")
        except ValueError:
            print("Please enter a valid number.")

    base_model_name = model_names.pop(base_model_idx)
    print(f"\nSelected base model: '{base_model_name}'")

    cumulative_f3d = all_models_data[base_model_name]['f3d'].copy()
    cumulative_r3d = all_models_data[base_model_name]['r3d'].copy()

    previous_model_data = all_models_data[base_model_name]
    remaining_models_to_splice = model_names
    print("Splice order:", " -> ".join([base_model_name] + remaining_models_to_splice))

    for attach_model_name in remaining_models_to_splice:
        print(f"\n--- Splicing '{previous_model_data['name']}' + '{attach_model_name}' ---")

        base_points = _find_splicing_points(
            previous_model_data['f3d'],
            previous_model_data['front_support_keys'],
            mode='bottom'
        )
        base_points.sort(key=lambda p: p[0])
        base_left, base_right = base_points[0], base_points[1]
        print(f"  - Base points: {base_left}, {base_right}")

        attach_model_data = all_models_data[attach_model_name]
        attach_points_orig = _find_splicing_points(
            attach_model_data['f3d'],
            attach_model_data['front_support_keys'],
            mode='top'
        )
        attach_points_orig.sort(key=lambda p: p[0])
        attach_left, attach_right = attach_points_orig[0], attach_points_orig[1]
        print(f"  - Attach points: {attach_left}, {attach_right}")

        current_attach_model_3d = {
            'f3d': attach_model_data['f3d'].copy(),
            'r3d': attach_model_data['r3d'].copy(),
        }
        _align_and_transform_model(
            current_attach_model_3d,
            source_p1=attach_left,
            source_p2=attach_right,
            target_p1=base_left,
            target_p2=base_right,
        )

        cumulative_f3d.update(current_attach_model_3d['f3d'])
        cumulative_r3d.update(current_attach_model_3d['r3d'])

        previous_model_data = {
            'name': attach_model_name,
            'f3d': current_attach_model_3d['f3d'],
            'r3d': current_attach_model_3d['r3d'],
            'front_support_keys': attach_model_data['front_support_keys'],
        }

    print("\n" + "=" * 50)
    print("Splicing complete")
    print("=" * 50)

    return cumulative_f3d, cumulative_r3d
# ====== Final Output (闂?generate_final_output.py) ======
# generate_final_output.py
import json
import numpy as np
from typing import Dict, List, Tuple

# 缂傚倸鍊风欢锟犲磻婢舵劦鏁嬬憸鏃堝箖濡ゅ懏鍊婚柦妯侯槺椤︻偄顪冮妶鍡楀闁搞劍妞藉畷鎰暦閸ワ絽浜鹃柣鐔哄閸熺偟鎲搁弶鍨殭闁挎洏鍨介、鏃堝醇濠靛浂妫熼梻浣规偠閸庡姊介崟顖ｆ晝闁伙絽澶囬崑鎾斥枔閸喗鐏€闂佺顑嗛幐鎼佲€﹂崸妤佸殝闁割煈鍋嗙粙鍥⒑娴兼瑧鎮奸柛瀣尵缁?
CoordMap: TypeAlias = Dict[str, Seg3D]
UniqueNodeDict: TypeAlias = Dict[Point3D, Dict[str, Any]]

TOLERANCE = 1e-4


class UniqueNodeIdentifier:
    """
    闂傚倷绀侀幖顐ょ矓閸洍鈧箓宕奸姀銏㈠闂佸憡鎸嗛崨顓熸濠电偞娼欓崥瀣偡瑜忕划鍫熷緞閹邦厼浠梺褰掑亰閸犳牠寮稿▎鎾寸厽妞ゆ挾鍣ュ▓婊呪偓瑙勬礃閼归箖鍩ユ径濞㈢喖鎳栭埡渚囨П闂傚倷鑳堕…鍫㈡崲閸儱绀夌€光偓閸曨剙鍓冲銈嗗笒鐎氼剟鎳滅憴鍕╀簻闁哄秲鍔庨幊鍛亜韫囨稐鎲鹃柡宀嬬秮婵℃悂濡烽妷顔荤磽濠电姷顣藉Σ鍛村矗閸愵喖绠栨繛鍡樻尰閸嬶繝鏌熷▓鍨灍闁规彃顭峰铏圭矙鐠恒劎顔掑┑鐐跺瀹曢潧危閹邦兘鏀介悗锝庡墮缁侊箓姊洪崗鍏煎€愭繛浣冲懎绶ら柣鐔诲焽閳ь剚甯掗～婵嬵敇閻斿摜绐欴闂傚倷绀侀幖顐ゆ偖椤愶箑纾块柟缁㈠櫘閺佸淇婇妶鍛櫣缂佲偓婢舵劖鐓熼柡鍐ㄦ祩閸ゆ瑩鏌涘Ο缁樺唉闁?
    - 闂傚倷绀佸﹢閬嶃€傛禒瀣；闁瑰墽绮悡娑㈡煕椤愶絿绠ラ柡鈧惌浼存⒒娴ｄ警娼掗柛鎰ㄦ櫇閻撴垹绱撻崒姘毙ｆ慨濠傛贡缁瑦寰勯幇顑跨炊闂佸憡娲﹂崢浠嬪箟閼姐倗纾藉ù锝堫嚃濞堬絿绱撻崒娑欑殤闁硅弓鍗冲畷鍗炍熼搹鍦嵁闂備礁鎲″ú锕傚储娴犲纾归柣鎰劋閻?
    """

    def __init__(self, final_coords: CoordMap, all_models_data: AllModelsData):
        self.final_coords = final_coords
        self.all_models_data = all_models_data
        self.unique_nodes: UniqueNodeDict = {}
        self.base_coord_to_info: Dict[Point3D, Dict] = {}

        self._build_unique_node_map()
        self._assign_base_ids_from_semantics()

    def _get_base_coord_q3(self, point: Point3D) -> Point3D:
        x, y, z = point
        base_x = -abs(x) if abs(x) > TOLERANCE else 0.0
        base_y = -abs(y) if abs(y) > TOLERANCE else 0.0
        return (base_x, base_y, z)

    def _build_unique_node_map(self):
        all_points_info = []
        for mid_orig, seg in self.final_coords.items():
            mid = mid_orig.replace("F_", "").replace("R_", "")
            is_support = any(mid in m.get('ganjian_args', {}).get('front_support', {}) or \
                             mid in m.get('ganjian_args', {}).get('right_support', {}) \
                             for m in self.all_models_data.values())
            p1, p2 = seg
            if abs(p1[2] - p2[2]) < TOLERANCE:
                suffix1, suffix2 = ("10", "20") if p1[0] < p2[0] else ("20", "10")
            else:
                suffix1, suffix2 = ("10", "20") if p1[2] < p2[2] else ("20", "10")
            all_points_info.append({"coord": tuple(p1), "mid": mid, "is_support": is_support, "suffix": suffix1})
            all_points_info.append({"coord": tuple(p2), "mid": mid, "is_support": is_support, "suffix": suffix2})
        for p_info in all_points_info:
            found_match = False
            for unique_coord in self.unique_nodes.keys():
                if np.linalg.norm(np.array(p_info["coord"]) - np.array(unique_coord)) < TOLERANCE:
                    self.unique_nodes[unique_coord]["members"].append(p_info)
                    found_match = True
                    break
            if not found_match:
                self.unique_nodes[p_info["coord"]] = {"members": [p_info]}

    def _assign_base_ids_from_semantics(self):
        semantic_base_coords = set()
        for model_data in self.all_models_data.values():
            identifiers = model_data.get('base_node_identifiers')
            if not identifiers: continue

            left_support_id = identifiers.get('left_support_id')
            if left_support_id and left_support_id in self.final_coords:
                semantic_base_coords.update(map(tuple, self.final_coords[left_support_id]))

            for horiz_id in identifiers.get('horizontal_ids', []):
                if horiz_id in self.final_coords:
                    p1, p2 = self.final_coords[horiz_id]
                    left_endpoint = tuple(p1) if p1[0] <= p2[0] else tuple(p2)
                    semantic_base_coords.add(left_endpoint)

        for coord in semantic_base_coords:
            found_node_coord = None
            for unique_coord in self.unique_nodes.keys():
                if np.linalg.norm(np.array(coord) - np.array(unique_coord)) < TOLERANCE:
                    found_node_coord = unique_coord
                    break
            if not found_node_coord: continue

            data = self.unique_nodes[found_node_coord]
            support_members = [m for m in data["members"] if m["is_support"]]
            owner = support_members[0] if support_members else data["members"][0]
            is_support_node = any(m['is_support'] for m in data["members"])

            id_prefix_str = ''.join(filter(str.isdigit, owner["mid"]))
            # 婵犵數鍎戠徊钘壝归崒鐐茬獥婵°倕鎳庨弸浣糕攽閸屾碍鍟為柛? 闂傚倷鑳堕崕鐢稿疾濞戙垺鍋ら柕濞у嫭娈伴梺鍦檸閸犳宕戦妸鈺傜厽闁哄啫鍋嗛悞楣冩煟韫囨挻鍠橀柟顔筋殔閳藉鈻庡Ο鑽ゆ毉婵＄偑鍊栭崹鎶芥倿閿斿墽鐭欏鑸靛姈閸庢捇鏌?
            base_id = f"{id_prefix_str}{owner['suffix']}"

            self.base_coord_to_info[found_node_coord] = {"id": base_id, "is_support": is_support_node}

    def get_node_id(self, point: Point3D) -> str:
        theoretical_base_coord = self._get_base_coord_q3(point)
        if not self.base_coord_to_info: return "-1"

        actual_base_coord = min(self.base_coord_to_info.keys(),
                                key=lambda bc: np.linalg.norm(np.array(bc) - np.array(theoretical_base_coord)))

        info = self.base_coord_to_info.get(actual_base_coord)
        if info is None: return "-1"

        # 婵犵數鍎戠徊钘壝归崒鐐茬獥婵°倕鎳庨弸浣糕攽閸屾碍鍟為柛? 闂傚倷绀佸﹢閬嶃€傛禒瀣；闁瑰墽绮悡娑㈡煕椤愶絿绠ラ柡鈧惌浼存⒒娴ｇ儤鍤€闁诲繑绻勭划鏂跨暦閸モ晝顦梺鍝勫暙閻楀棝寮伴妷鈺佺骇闁绘劖娼欓ˉ瀣煠瑜版帞鐣洪柟顔筋殔閳藉鈻庡Ο鑽ゆ毉婵＄偑鍊栭崹鎶芥倿閿斿墽鐭?
        base_id_str = info['id']
        x, y, z = point
        is_right = abs(x) > TOLERANCE and x > 0
        is_front = abs(y) > TOLERANCE and y > 0

        # 闂備浇顕х换鎰崲閹邦儵娑樜旈崨顔间槐閻熸粌绻掗崚鎺楊敇閵忊剝娅嗛梺鍏煎墯閸ㄧ厧煤椤掑嫭鐓涘璺鸿嫰閸撻亶鏌涜箛鏃傘€掗柟宄扮秺閹垽鎮℃惔銏⑩偓顒勬煟鎼淬垻鈯曢拑杈ㄧ箾閸繄鍩ｇ€殿喖鐖奸崺锟犲磼濠婂海浼囨俊鐐€戦崹娲垂瑜版帒绠悗锝庡枟閺咁剟鏌涢弴銊ュ箺婵絽鐗撳娲箰鎼达絺妲堥梺鍏兼た閸ㄨ泛鐣烽鐐茬劦妞ゆ帒瀚痪褔鏌ｉ幋婵囶棞濠⒀屽枟缁绘盯宕ｆ径灞解拡闂侀€炲苯澧紒瀣浮閵嗗啴宕奸妷顔芥櫈婵炶揪绲藉﹢閬嶅煝?
        try:
            base_id_num = int(base_id_str)
            if is_right and not is_front:
                return str(base_id_num + 1)
            elif not is_right and is_front:
                return str(base_id_num + 2)
            elif is_right and is_front:
                return str(base_id_num + 3)
            else:
                return base_id_str
        except ValueError:
            return base_id_str  # 婵犵數濮烽。浠嬪焵椤掆偓閸熷潡鍩€椤掆偓缂嶅﹪骞冨Ο鑽ょ畽闁革附鐗楃换娑㈠箣閻愭潙纰嶇紓浣割樀濞佳冨祫闂佸憡绺块崕鍐参涢娑栦簻闁哄秲鍔庨埊鏇熺箾閸繄鍩ｉ柟顔筋殔閳藉鈻庡Ο娲诲悈缂傚倷娴囨ご鍝ユ崲閸儱绠氶柛鏇ㄥ幐閸嬫挸鈽夊▍顓т簼瀵板嫬顓兼径濠勯獓闂佸啿鎼崐褰掓偂閵夛妇绠?



# === Paste the following into core.py (replace the old generate_outputs and add helpers) ===
from typing import Dict, List, Tuple
import math

# 缂傚倸鍊风欢锟犲磻婢舵劦鏁嬬憸鏃堝箖濡ゅ懏鍊婚柦妯侯槺椤︻偄顪冮妶鍡楀闁搞劍妞藉畷鎰暦閸ワ絽浜鹃柣鐔哄閸熺偟鎲搁弶鍨殭闁挎洏鍨介、鏃堝醇濠靛浂妫熼梻浣规偠閸庡姊介崟顖ｆ晝闁伙絽澶囬崑鎾斥枔閸喗鐏€闂佺顑嗛幐鎼佲€﹂崸妤佸殝闁割煈鍋嗙粙鍥⒑娴兼瑧鎮奸柛瀣尵缁?

# ---------- helpers (small, internal) ----------
# ===== helper: 闂傚倷绀侀幖顐︻敄閸涱垪鍋撳鐓庡缂?pinjie闂傚倷鐒︾€笛呯矙閹达附鍋嬪┑鐘叉祩閺佸棙绻濇繝鍌滃妞ゃ儱鐗撻弻鏇＄疀閵壯呅ｅ┑鐐插悑鐢繝寮诲☉銏犖ㄧ憸宥嗙閹岀唵鐟滃秶绮旈悷閭﹀殨闁割煈鍋勭欢鐐烘倵閿濆懏濯奸柛娆忓暙閻ｇ兘濡烽埡浣侯吅闂佺粯鍔曢顓犵矓閾忣偆绠鹃悗鐢殿焾瀛濇繝鈷€鍐弰妞ゃ垺妫冮、妤呭礋椤掆偓閳ь剛鍏橀弻锝堫槻闁硅姤绮庣划鍫熷緞瀹€鈧壕钘壝归敐鍛础缂佺姵鎸婚妵鍕即閵娿儲鐝濋悗瑙勬礃閹倿鐛崶顒夋晣闁绘灏欐导鍥⒒娴ｇ懓顕滅紒瀣笧缁瑩骞掑Δ浣哄姼闂侀潧艌閺呮粓宕?ID 婵犵數濮伴崹鐓庘枖濞戞氨鐭撻柛顐ｆ礀閺嬩線鏌曢崼婵囧闁哥姴妫濋弻娑㈠即閵娿儰绨婚梺璇茬箳閸犳牠寮婚妸銉㈡婵炲棙鍨熸慨鍥煟?Z闂? X闂?闂傚倷绀佸﹢閬嶅磿閵堝洦鏆滈柟鐑樻婵櫕銇勯幘鍗炵仾闁?=====
def _build_pinjie_from_front_horiz(final_coords_map: dict,
                                   all_models_data: dict,
                                   ganjian: list) -> list:
    """
    闂備礁鎼ˇ顐﹀疾濠婂牆钃熼柕濞垮剭?pinjie: List[[node_id(str), [x,y,z]]]
    闂備浇宕甸崰鎰版偡閵壯€鍋撳鐓庡⒋鐎规洖缍婇、娑㈡倷鐎涙ɑ鐝?
      - 婵犵數鍋涢顓熸叏閹绢喖绠犻煫鍥ㄧ☉閺嬩胶鎲搁悧鍫濈瑲闁抽攱鐗犻弻娑㈠灳瀹曞洨鐣鹃梺绋款儐閹告悂鈥﹂妸鈺佺闂傚牊绋戣灇闂傚倸鍊搁崐鎼佹偋閸曨垰鍨傚┑鍌炴交缂嶆牠鎮楅敐搴℃灈闁绘劕锕鍝勨枎閹呬粴闂佺顑嗛幐鎼佸煘閹达箑閱囬柣鏃傚劋濞堟悂姊绘担鍛婅础妞わ絼绮欏畷鎴﹀箻缂佹鍘搁梺鍓插亝缁诲秴危瑜版帗鐓ｉ柛鈩冪⊕閻撴洘鎱ㄥ鍡楀箹闁诲骏闄勭换娑㈡偂鎼淬垺鎷辩紓浣稿€圭敮鈥崇暦濠婂嫮鐟归柛銉绾句粙姊绘担铏瑰笡闁告梹顨呴埢宥夊閵忊槅娼?
      - 缂傚倸鍊烽悞锕€螞韫囨稑鍨傞柟鎯版绾?ID 婵犵數鍋為崹鍫曞箰閸洖纾块柡灞诲劜閸嬪绱掔€ｎ亞姘ㄩ柡宀嬬畵閹綊骞侀幒鎴濐瀴闂?ganjian 婵犵數鍋為崹鍫曞箹閳哄懎鐭楅柍褜鍓氶妵鍕即閻斿嘲鎽甸悗娈垮枛閻栫厧鐣烽柆宥呭嵆闁绘洑绀佹禒铏圭磽閸屾瑧鍔嶆俊顐㈢箻瀹曞綊骞庨挊澶岋紱闂佹寧绻傞ˇ浼村磿?node1_id/node2_id闂傚倷鐒︾€笛呯矙閹达附鍋嬮柛娑卞灠閸ㄦ繈鏌ｅΟ鑲╁笡闁搞倐鍋撻柣搴″帨閸嬫捇鏌嶈閸撶喖鐛€ｎ喗鍊婚柦妯侯槺椤撳ジ姊洪崜鑼帥闁革綆鍠栧嵄濠电姵纰嶉悡鐔搞亜椤愵偄澧┑顔瑰亾婵＄偑鍊ら崑鍕囬棃娑氭殾婵﹩鍏橀弸搴㈢箾閸℃ê鐏╂い锔诲亰濮?
      - 闂備礁鎼ˇ顖炴偋婵犲洤绠伴柟闂寸閸氳銇勯幘璺盒ョ痪鎯у悑缁绘繈妫冨☉娆欑礊闂佹悶鍊楁繛鈧柡灞剧椤︽娊鏌涢弮鈧悧鐘诲箖閵夆晜鏅插璺侯儐濞呮牠姊虹粔鍡楀椤al_coords_map 婵犵數鍋為崹鍫曞箹閳哄懎鍌ㄩ柟顖嗏偓閺?3D 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻浣虹帛閻楊厾绱炴笟鈧顐㈩吋閸℃绐炲┑鐐村灦閼归箖鎳?
      - 闂傚倷绀侀幉锟犳晪濡炪値鍘鹃崗妯虹暦閹惰棄绠瑰ù锝堫潐濞呮牕鈹戦鏂や緵闁告挻宀稿畷鎰板础閻愨晜顫嶉梺鍦檸閸ㄧ増绂?node_id 闂傚倷绀侀幉锟犳偡椤栨稓顩叉繛鍡樺灦瀹曞弶鎱ㄥΟ鍨厫闁稿鏅滅换娑㈠幢濡や焦宕冲銈呯箺妞村摜鎹㈠☉銏犲耿闊洦妫忓鎰磽?
      - 闂傚倷绀佸﹢閬嶅磿閵堝洦鏆滈柟鐑樻婵櫕銇勯幘鍗炵仾闁哄拋鍓氶幈銊ヮ潨閸℃绠归梺?Z 闂傚倷绀侀幉锟犮€冮崨顒兼椽濡堕崶顏勑″銈嗘尪閸ㄦ椽寮查鍕€堕柣鎰煐椤ュ鏌￠崨顔炬噰闁?X 闂傚倷绀侀幉锟犮€冮崨顒兼椽濡堕崶顏勑″銈嗘尪閸ㄧ绻?
    """
    # 1) 闂傚倷绀侀幉锟犳偡閿曞倹鍋嬮柡鍥ュ灩閸氳銇勯幘鍗炵仼缂佺姰鍎甸弻宥堫檨闁告挾鍠庨锝夊垂椤愩垻绐為梺绯曗偓宕囩濞存粎鍋撶换婵囩節閸屾凹浼岄梺鍛婃煛閸嬫捇姊婚崒姘偓鎼佹偋閸曨垰鍨傛繛宸簼閹酣姊绘担鍛婂暈缁炬澘绉瑰畷鍦崉娓氼垳鍔烽柣蹇曞仜婢т粙銆呴悜鑺ョ厱闁靛濡囬埢鎾绘煕鐎ｎ偅灏柍瑙勫灴瀹曞ジ鎮㈤悜妯活啅闂傚倷绀侀幉锟犫€﹂崶顒€绐楅幖鎼厜缂?ID闂傚倷鐒︾€笛呯矙閹达附鍋嬪┑鐘插亰閼版寧銇勯幘璺盒ｉ柡鍡樼矒閺屻劑寮崶顭戞濡炪倕绻愰…鐑藉蓟閻旂厧绠掗柟鐑樺灥婵酣姊虹拠鈥虫灍妞ゃ劌鐗忓Σ鎰板箻鐠囪尙鍔﹀銈嗗笒鐎氼參寮?
    front_h_ids = set()
    for m in (all_models_data or {}).values():
        ga = (m or {}).get('ganjian_args', {}) or {}
        fh = ga.get('front_horizontal') or {}
        for mid in fh.keys():
            front_h_ids.add(str(mid))

    if not front_h_ids:
        return []

    # 2) 闂佽娴烽崑锝夊磹濞戞ǚ鏋嶉柨婵嗩槹閸?闂傚倷鑳堕崑銊╁磿閼碱剛绠旀慨濠冩▍ber_id -> (node1_id, node2_id)闂?闂傚倷绀侀幖顐も偓姘煎枟閹便劑骞橀钘夊壄闂佺粯顭囩划顖炲疾椤掑嫭鐓曟い鎰╁€曢弸鎴︽⒒閸曨偆效闁?ganjian闂?
    m_to_nodes = {}
    for g in (ganjian or []):
        mid = str(g.get('member_id'))
        n1  = str(g.get('node1_id'))
        n2  = str(g.get('node2_id'))
        if mid and (n1 is not None) and (n2 is not None):
            m_to_nodes[mid] = (n1, n2)

    # # 3) 闂?final_coords_map 婵犵數鍋為崹鍫曞箹閳哄懎鍌ㄩ柧蹇撴贡缁?front_h_ids 闂傚倷绀侀幉锟犳偋閺囩姷绀婂┑鐘叉搐閸屻劑鏌曢崼婵愭Ч闁稿骸绉归弻娑㈠即閻愬樊鏆㈢紓浣插亾闁告洦鍨遍悡鐘绘煛婢跺﹦浠㈤柡鍡愬灪娣囧﹪骞嗚閻撳吋顨ラ悙鑼鐎规洘顨婇幃鈩冩償閳藉棙些婵犵數鍋涢悺銊х尵閸岀偛宸濇い鏃囧Г椤忕喖姊绘担鍦菇闁告柨鐬奸埀顒佸嚬閸撶喖鐛崘銊庢棃宕橀鍡闯闂?_1/_2闂傚倷鑳堕崑銊╁磿閼姐倖濯奸柨婵嗘处椤洘鎱ㄥΟ鍨厫闁绘帡绠栭弻锕€螣娓氼垱笑濡炪値鍋撶紞渚€寮?
    # #    闂傚倷绀侀幉锟犳偋閺囩姷绀婂┑鐘叉搐閸屻劑鏌曢崼婵愭Ц婵☆偅锕㈤弻锝夋偄缁嬫妫嗙紒缁㈠幐閸嬫捇姊绘担鐟邦嚋缂佸甯￠幆宀勵敊閻ｅ矈娲?闂傚倷鑳堕崑銊╁磿閼碱剙鍨濈€光偓閸曨厼绁﹂梺瑙勫礃椤曆呯不閸愬樊鐔嗛悹铏瑰皑閺€濠氭煕婵犲嫭鏆╃紒杈ㄦ崌瀹曟帒螖閳ь剚绂嶆ィ鍐┾拺婵懓娲ゆ俊濂告倵濮樼厧澧撮柟顔哄灲閸┾偓?ID = k.split('_')[0]闂?婵?front_h_ids 濠电姵顔栭崳顖滃緤閹灛娑欐媴閻戞﹩鍋?
    # def _base_id(k: str) -> str:
    #     return str(k).split('_', 1)[0]
    # 闂傚倷鑳堕幊鎾绘倶濮樿泛纾块柟鎯版閺?_base_id 闂傚倷绀侀幖顐﹀磹娴犲缍栧璺烘湰閸?
    def _base_id(k: str) -> str:
        # 闂傚倷绀侀幖顐﹀磹閻熼偊鐔嗘慨妞诲亾鐠侯垶鏌涢幇闈涙灈闁稿被鍔岄埞鎴︽偐瀹曞浂鏆￠梺?F_ 闂?R_ 闂傚倷鐒﹂惇褰掑礉瀹€鈧埀顒佸嚬閸撶喖骞冩ィ鍐ㄎ╅柍杞拌兌椤ρ囨⒑闂堟侗鐒鹃柛鏂挎捣缁寮介妸褏鐦?
        k = str(k).replace("F_", "").replace("R_", "")
        return k.split('_', 1)[0]

    # 4) Collect endpoints by horizontal member, not by globally de-duplicated
    # node id. The stretcher interface consumes pinjie in groups of four:
    # two adjacent horizontal rods, each with left/right endpoints.
    horizontal_items = []
    seen_member_keys = set()
    for k, seg in (final_coords_map or {}).items():
        base = _base_id(k)
        if base not in front_h_ids:
            continue
        member_key = str(k)
        if member_key in seen_member_keys:
            continue
        if not isinstance(seg, (list, tuple)) or len(seg) != 2:
            continue

        node_ids = m_to_nodes.get(str(k))
        if node_ids is None:
            node_ids = m_to_nodes.get(base)
        if node_ids is None:
            continue

        n1, n2 = node_ids
        p1, p2 = seg
        c1 = [float(p1[0]), float(p1[1]), float(p1[2])]
        c2 = [float(p2[0]), float(p2[1]), float(p2[2])]
        endpoints = [(str(n1), c1), (str(n2), c2)]
        endpoints.sort(key=lambda item: item[1][0])
        z_avg = (c1[2] + c2[2]) / 2.0
        x_avg = (c1[0] + c2[0]) / 2.0
        horizontal_items.append((z_avg, x_avg, member_key, endpoints))
        seen_member_keys.add(member_key)

    # 5) Sort by tower height, then lateral position/member id for stability.
    horizontal_items.sort(key=lambda item: (item[0], item[1], item[2]))

    # 6) Flatten back to the legacy pinjie structure.
    pinjie = []
    for _, _, _, endpoints in horizontal_items:
        for node_id, coord in endpoints:
            pinjie.append([node_id, coord])
    return pinjie

def _last2(s: str) -> str:
    return s[-2:] if len(s) >= 2 else s

def _base(s: str) -> str:
    return s[:-2] if len(s) >= 2 and s[-2:].isdigit() else s

def _plus_suffix(s: str, delta: int) -> str:
    suf = _last2(s)
    if not suf.isdigit():
        return s
    n = int(suf) + delta
    return f"{_base(s)}{n:02d}"

def _sym_pt(pt: Point3D, sym_type: int) -> Point3D:
    x, y, z = pt
    if sym_type == 1:   # 闂佽楠哥紞濠傤焽閼姐倗涓嶉柟杈剧祷娴?
        return (-x, y, z)
    if sym_type == 2:   # 闂傚倷绀侀幉锟犲箰閸濄儳鐭撻柟缁㈠枛缁?
        return (x, -y, z)
    if sym_type == 3:   # 婵犵數鍋為崹鍫曞箹閳哄懎鍌ㄩ柤娴嬫櫇缁?
        return (-x, -y, z)
    return pt           # 4: 闂傚倷鑳堕崢褔銆冩惔銏㈩洸闁挎繂顦伴ˉ濠囨煃閸濆嫭鍣洪柡鍜佸墴閺屾盯顢曢敐鍥╃厒缂備胶濮崇划娆撳蓟閻斿吋鈷愰柟閭﹀弾濡倻绱撴担璇℃當妞わ箓娼ч悾宄扳攽鐎Ｑ€鍋撻敃鍌氱闁哄啫鍋嗗Σ?

def _dist3(a: Point3D, b: Point3D) -> float:
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

def _sort_lr(p1: Point3D, p2: Point3D) -> Tuple[Point3D, Point3D]:
    # 婵?x 婵犵數鍋為崹鍫曞箲娴ｅ壊娴栭柕濞р偓閸嬫捇妫冨☉姘卞姱闂佽桨绀佺粔鍫曞焵?婵犵數鍋為崹鍫曞箰妤ｅ啫纾块柕鍫濐樈閺佸啫鈹戦崒姘暈闁哄拋鍓熼幃姗€鎮欑捄杞版睏缂備胶濮崇划娆撳箖?(left, right)
    if (p1[0], p1[1]) <= (p2[0], p2[1]):
        return p1, p2
    return p2, p1

def _top_bottom(p1: Point3D, p2: Point3D) -> Tuple[Point3D, Point3D]:
    # z 闂備胶鍎甸崜婵堟暜閹烘鏅濋柕鍫濐槹閸庡秵銇勯幒鎴濃偓褰掑箚閵夈儮鏀介柣妯哄级婢跺嫭绻涢弶鎴烆棞闁?
    if p1[2] <= p2[2]:
        return p1, p2
    return p2, p1

def _closest_id(pt: Point3D, known: Dict[str, Point3D], eps=1e-6) -> str:
    for k, v in known.items():
        if _dist3(pt, v) <= eps:
            return k
    return ""


def _reference_value(node_id: str) -> str:
    """Encode a node reference using the same leading-1 format as single view."""
    return f"1{str(node_id)}"


def _reference_node_values(pt: Point3D, ref_ids: Tuple[str, str], ref_seg: List[Point3D]) -> Dict[str, object]:
    """
    Build a node_type=12 coordinate payload.

    Two coordinate fields hold node references and the remaining field stores
    the real coordinate value along the strongest axis of the host rod.
    """
    axis_names = ("X", "Y", "Z")
    if ref_seg and len(ref_seg) >= 2:
        deltas = [abs(ref_seg[1][i] - ref_seg[0][i]) for i in range(3)]
        real_axis = max(range(3), key=lambda i: deltas[i])
        if deltas[real_axis] <= 1e-8:
            real_axis = 2
    else:
        real_axis = 2

    ref_iter = iter((_reference_value(ref_ids[0]), _reference_value(ref_ids[1])))
    values: Dict[str, object] = {}
    for idx, axis_name in enumerate(axis_names):
        if idx == real_axis:
            values[axis_name] = round(pt[idx], 3)
        else:
            values[axis_name] = next(ref_iter)
    return values





def generate_outputs(final_coords_map: Dict[str, List[Point3D]], all_models_data: Dict[str, dict]):
    """
    缂傚倸鍊搁崐椋庣矆娓氣偓閹勭節閸ャ劌鈧灚銇勯幒宥堝厡闁崇懓绉甸妵鍕籍閸屾粍鎲橀梺鍛婃煛閸嬫捇姊绘担铏瑰笡妞ゃ劌鎳橀幃褔鎮欓崹顐綗婵炲鍘ч悺銊╁磿鎼淬劍鍊垫繛鎴烆仾椤忓懎绶炵€广儱顦痪褔鏌涢銈呮瀾閻忓浚鍙冮弻娑㈠Χ鎼粹€崇缂備浇椴哥敮鎺楀煘閹达箑骞㈤柍杞扮劍椤?3D 闂傚倷鑳堕～瀣礋椤愩埄娼旈梻?(node_type: 11)闂?
    闂備礁婀遍崢褔顢氶銏犵獥閹艰揪绲鹃～鏇㈡煛閸愩劌鈧敻宕戦幘瀛樺闁告劦鐓堝Λ鍫ユ⒑閹肩偘绱橀柛銉戝洦鏆呴梻浣哥秺閸嬪﹪宕㈡ィ鍐ㄥ瀭闁绘挸绨跺Σ鍫ユ煙閸撗勫殌缂佹唻濡囩槐鎾愁吋閸涱喖娈楅悗瑙勬处娴滅偞绂掗敃鍌氱畾妞ゎ剦鍣崑濠囧蓟閳╁啫绶為柛鈩冦仦婢规洟姊婚崒娆愮グ闁跨喆鍎靛畷鏇熸綇閳规儳浜鹃悷娆忓閳绘洟鏌?node_type: 12 闂佽瀛╅鏍窗濡も偓鐓ゆ繝濠傜墕閺嬩線鏌曢崼婵愭Ц缂佲偓閸愨晝绠鹃柛鈩兠慨澶愭煏閸℃韬柡?
    """
    ganjian: List[dict] = []
    jiedian: List[dict] = []
    pinjie: List[list] = [] 

    EPS = 150.0

    for stem, pack in all_models_data.items():
        args = pack.get("ganjian_args", {})
        front_support: Dict[str, list] = {str(k): v for k, v in (args.get("front_support") or {}).items()}
        right_support: Dict[str, list] = {str(k): v for k, v in (args.get("right_support") or {}).items()}
        front_horizontal: Dict[str, list] = {str(k): v for k, v in (args.get("front_horizontal") or {}).items()}
        right_horizontal: Dict[str, list] = {str(k): v for k, v in (args.get("right_horizontal") or {}).items()}
        front_x: Dict[str, list] = {str(k): v for k, v in (args.get("front_x_fixed") or {}).items()}
        right_x: Dict[str, list] = {str(k): v for k, v in (args.get("right_x_fixed") or {}).items()}
        reference_tiers = {
            "F": args.get("front_reference_tiers") or {},
            "R": args.get("right_reference_tiers") or {},
        }
        member_nodes: Dict[Tuple[str, str], Tuple[str, str]] = {}
        member_points: Dict[Tuple[str, str], Tuple[Point3D, Point3D]] = {}

        def _tier_for(view_tag: str, member_id: str) -> str:
            tiers = reference_tiers.get(view_tag) or {}
            member_id = str(member_id)
            if member_id in (tiers.get("tier2") or set()):
                return "tier2"
            if member_id in (tiers.get("tier3") or set()):
                return "tier3"
            return "tier1"

        def _host_for_endpoint(view_tag: str, member_id: str, endpoint_index: int):
            tiers = reference_tiers.get(view_tag) or {}
            hosts = (tiers.get("endpoint_hosts") or {}).get(str(member_id)) or []
            if endpoint_index < len(hosts):
                return hosts[endpoint_index]
            return None

        def _register_node(
            node_id: str,
            pt: Point3D,
            view_tag: str,
            member_id: str,
            endpoint_index: int,
            force_real: bool = False,
        ) -> None:
            if force_real or _tier_for(view_tag, str(member_id)) == "tier1":
                jiedian.append({
                    "node_id": node_id,
                    "node_type": 11,
                    "X": round(pt[0], 3),
                    "Y": round(pt[1], 3),
                    "Z": round(pt[2], 3),
                    "symmetry_type": 4,
                })
            else:
                host = _host_for_endpoint(view_tag, str(member_id), endpoint_index) or {}
                host_key = (view_tag, str(host.get("host", "")))
                ref_ids = member_nodes.get(host_key)
                ref_seg = member_points.get(host_key)
                if not ref_ids or not ref_seg:
                    jiedian.append({
                        "node_id": node_id,
                        "node_type": 11,
                        "X": round(pt[0], 3),
                        "Y": round(pt[1], 3),
                        "Z": round(pt[2], 3),
                        "symmetry_type": 4,
                    })
                else:
                    values = _reference_node_values(pt, ref_ids, list(ref_seg))
                    jiedian.append({
                        "node_id": node_id,
                        "node_type": 12,
                        "X": values["X"],
                        "Y": values["Y"],
                        "Z": values["Z"],
                        "symmetry_type": 4,
                    })

            known_nodes[node_id] = pt
            known_nodes[_plus_suffix(node_id, +1)] = _sym_pt(pt, 1)
            known_nodes[_plus_suffix(node_id, +2)] = _sym_pt(pt, 2)
            known_nodes[_plus_suffix(node_id, +3)] = _sym_pt(pt, 3)

        def _remember_member(
            view_tag: str,
            member_id: str,
            node1_id: str,
            node2_id: str,
            p1: Point3D,
            p2: Point3D,
        ) -> None:
            member_key = (view_tag, str(member_id))
            member_nodes[member_key] = (str(node1_id), str(node2_id))
            member_points[member_key] = (p1, p2)

        # === 1) 闂傚倷鑳剁涵鍫曞疾濞戙垹绠规い鎰剁畱闂傤垱銇勯弽顐粶缂備讲鏅滈妵鍕冀閵娧€濮囬柣搴㈣壘閵堟悂寮婚悢铏圭＜婵☆垰鎼～宀勬偡?===
        base_sid = None
        min_cx = None
        for sid in front_support.keys():
            seg3d = final_coords_map.get(f"F_{sid}") 
            # seg3d = final_coords_map.get(str(sid))
            if not seg3d: continue
            cx = 0.5*(seg3d[0][0] + seg3d[1][0])
            if (min_cx is None) or (cx < min_cx):
                min_cx = cx
                base_sid = str(sid)
        if not base_sid: continue

        # pA, pB = final_coords_map[base_sid]
        pA, pB = final_coords_map[f"F_{base_sid}"]
        topP, botP = _top_bottom(pA, pB)
        sid10 = f"{node_id_base(base_sid)}10"
        sid20 = f"{node_id_base(base_sid)}20"

        known_nodes: Dict[str, Point3D] = {
            sid10: topP, sid20: botP,
            _plus_suffix(sid10, +1): _sym_pt(topP, 1),
            _plus_suffix(sid10, +2): _sym_pt(topP, 2),
            _plus_suffix(sid10, +3): _sym_pt(topP, 3),
            _plus_suffix(sid20, +1): _sym_pt(botP, 1),
            _plus_suffix(sid20, +2): _sym_pt(botP, 2),
            _plus_suffix(sid20, +3): _sym_pt(botP, 3),
        }

        # 闂備礁鎼ˇ顖炴偋婵犲洤绠伴柟闂寸閸氳銇勯幘鍗炵仼缂備讲鏅滈妵鍕冀閵娧€濮囬柣搴㈣壘閵堟悂寮诲☉銏犵厸濞达綀顫夐崕鎾绘⒑闂堚晝绉甸柛銊ョ埣楠炲﹪鎮欓崫鍕紲濠电姴锕ら崯鈺呭礌?(Type 11)
        _register_node(sid10, topP, "F", base_sid, 0, force_real=True)
        _register_node(sid20, botP, "F", base_sid, 1, force_real=True)
        _remember_member("F", base_sid, sid10, sid20, topP, botP)
        ganjian.append({"member_id": base_sid, "node1_id": sid10, "node2_id": sid20, "symmetry_type": 4})

        # === 婵犵數鍎戠徊钘壝归崒鐐茬獥闁哄稁鍘旈崶顒€钃熼柕澶涢檮濞呮牕鈹戦鐭亞澹曢鐘电濠电姵纰嶉悡鏇㈡煙鐎电孝闁告柨顑呴…鑳槻缂佸鎳撻锝夊垂椤愩垻绐炴繝鐢靛Т閸婂摜娆㈤鐔虹閻庣數顭堟牎闂佺粯顨嗛〃濠傤嚕椤愶富鏁嬮柍褜鍓熼悰顔碱潨閳ь剟鐛€ｎ喗鍊烽悗闈涙憸灏忔繝?===
        for sid in front_support.keys():
            if str(sid) == base_sid:
                continue  # 闂備浇宕垫慨鎾箹椤愶附鍋柛銉㈡櫆瀹曟煡鏌涢幇鐢靛帥闁哥喎鎳橀弻鐔虹磼濡桨鍒婂┑鈩冪叀娴滃爼寮婚敐澶嬪€烽柛娆忣樈濡倕鈹戦悙鑼闁搞劌鐏濋悾宄懊洪鍕炊闂佸憡娲﹂崑鍛存偟椤栫偞鈷戦悶娑掆偓鍏呭婵＄偑鍊栭悧妤冪矙閹烘柡鍋?
            # seg3d = final_coords_map.get(str(sid))
            seg3d = final_coords_map.get(f"F_{sid}") 
            if not seg3d:
                continue
            pA, pB = seg3d
            topP_other, botP_other = _top_bottom(pA, pB)
            sid10_other = f"{node_id_base(sid)}10"
            sid20_other = f"{node_id_base(sid)}20"
            
            # 濠电姷顣藉Σ鍛村磻閳ь剟鏌涚€ｎ偅宕岄柡宀嬬磿娴狅妇鎷犻幓鎺戭潥婵犵鈧啿绾ч柟顔煎€搁悾鐑藉Ψ閳哄倹娅嗛柣鐘充航閸斿酣骞夐崸妤佸€甸悷娆忓閹藉啴鎮樿箛鏃傛噰闁诡噯绻濋弫鎾绘偐閸愬弶鐤呴梻浣侯焾閺堫剛鍒掔仦鍓ь浄妞ゆ牜鍋為埛鎴︽煙缂佹ê绗х€涙繈姊虹拠鈥虫灈闂佸府缍佸顐㈩吋婢跺﹪鍞跺┑鐘茬仛閸旀牔绨洪梻鍌欑劍閻綊宕洪崟顖涘亗濠㈣泛鏈～?
            reuse_top = _closest_id(topP_other, known_nodes, eps=EPS)
            reuse_bot = _closest_id(botP_other, known_nodes, eps=EPS)
            
            if not reuse_top:
                _register_node(sid10_other, topP_other, "F", str(sid), 0)
                node1_id = sid10_other
            else:
                node1_id = reuse_top
            
            if not reuse_bot:
                _register_node(sid20_other, botP_other, "F", str(sid), 1)
                node2_id = sid20_other
            else:
                node2_id = reuse_bot
            _remember_member("F", str(sid), node1_id, node2_id, topP_other, botP_other)
            ganjian.append({"member_id": str(sid), "node1_id": node1_id, "node2_id": node2_id, "symmetry_type": 4})

        # === 婵犵數鍎戠徊钘壝归崒鐐茬獥闁哄稁鍘旈崶顒€钃熼柕澶涢檮濞呮牕鈹戦鐭亞澹曢鐘电濠电姵纰嶉悡鏇㈡煙鐎电孝闁告柨顑呴…鑳槻缂佸鎳撻锝夊垂椤愩垻绐炴繝鐢靛Т閸婂藝閿旂晫绠鹃柟鎯ь嚟濞堜即鏌涢弴銊ュ婵炲牅鍗冲娲捶椤撶偘澹曢梺鎼炲姀濞夋盯鈥﹂崶鈺€娌柛鎾楀本绁?===
        for rid in right_support.keys():
            # seg3d = final_coords_map.get(str(rid))
            seg3d = final_coords_map.get(f"R_{rid}")
            if not seg3d:
                continue
            pA, pB = seg3d
            topP_r, botP_r = _top_bottom(pA, pB)
            rid10 = f"{node_id_base(rid)}10"
            rid20 = f"{node_id_base(rid)}20"
            
            # 濠电姷顣藉Σ鍛村磻閳ь剟鏌涚€ｎ偅宕岄柡宀嬬磿娴狅妇鎷犻幓鎺戭潥婵犵鈧啿绾ч柟顔煎€搁悾鐑藉Ψ閳哄倹娅嗛柣鐘充航閸斿酣骞夐崸妤佸€甸悷娆忓閹藉啴鎮樿箛鏃傛噰闁诡噯绻濋弫鎾绘偐閸愬弶鐤呴梻浣侯焾閺堫剛鍒掔仦鍓ь浄妞ゆ牜鍋為埛鎴︽煙缂佹ê绗х€涙繈姊虹拠鈥虫灈闂佸府缍佸顐㈩吋婢跺﹪鍞跺┑鐘茬仛閸旀牔绨洪梻鍌欑劍閻綊宕洪崟顖涘亗濠㈣泛鏈～?
            reuse_top_r = _closest_id(topP_r, known_nodes, eps=EPS)
            reuse_bot_r = _closest_id(botP_r, known_nodes, eps=EPS)
            
            if not reuse_top_r:
                _register_node(rid10, topP_r, "R", str(rid), 0)
                node1_id_r = rid10
            else:
                node1_id_r = reuse_top_r
            
            if not reuse_bot_r:
                _register_node(rid20, botP_r, "R", str(rid), 1)
                node2_id_r = rid20
            else:
                node2_id_r = reuse_bot_r
            _remember_member("R", str(rid), node1_id_r, node2_id_r, topP_r, botP_r)
            ganjian.append({"member_id": str(rid), "node1_id": node1_id_r, "node2_id": node2_id_r, "symmetry_type": 4})

        # === 2) 濠电姵顔栭崰妤冩崲閹邦喚绀婂ù锝呭閻掍粙鏌℃径搴殾闁绘梻鈷堥弫鍌炴煕閺囥劌澧柍?===
        def _sym1_partner(nid: str) -> str:
            """闂佽楠哥紞濠傤焽閼姐倗涓嶉柟杈剧祷娴滃綊鏌涘┑鍕姉闁稿鎹囧Λ鍐ㄢ槈濞嗘帞顢呴柣?sym_type=1)闂傚倷鐒﹂惇褰掑礉瀹€鈧埀顒佸嚬娴滅偛危閹伴偊鏁婇柦妯侯樈閸ゃ倗绱掗悙顒€鍔ゆい鎴濇嚀閻忔劙姊? 0闂?, 2闂?"""
            _m = {"0": "1", "1": "0", "2": "3", "3": "2"}
            return nid[:-1] + _m[nid[-1]] if nid and nid[-1] in _m else _plus_suffix(nid, +1)

        for hid in sorted(front_horizontal.keys(), key=lambda x: float(x)):
            # seg3d = final_coords_map.get(str(hid))
            seg3d = final_coords_map.get(f"F_{hid}")
            if not seg3d: continue
            L, R = _sort_lr(*seg3d)
            reuse_id = _closest_id(L, {sid10: topP, sid20: botP}, eps=EPS)
            
            if reuse_id:
                left_node_id = reuse_id  
            else:
                # 闂傚倷绶氬褍螞濞嗘挸绀夐柡鍥ュ灩閻鎲搁弮鍫濊摕闁靛ň鏅╅弫濠勭磽娴ｅ顏勵嚕閹稿海绡€闁靛骏绲剧涵鍓х磼婢跺﹦鍩ｇ€规洘鍨块弫鎰緞婵烆潿鍎甸弻鐔煎箹椤撶偟浠紓浣瑰姈椤ㄥ懘鍩ユ径鎰鐎规洖娉﹂垾鏂ユ斀闁绘劕寮堕崰姗€鏌?Type 12 闂傚倸鍊风欢锟犲磻閸℃ɑ鍙忛柣銏㈩焾閸ㄥ倹鎱ㄥΟ鎸庣【闂佽￥鍊濋弻鐔兼焽閿曗偓楠炴﹢鏌涢妸褍甯堕柍钘夘樀楠炴﹢鎮烽幍顔碱槱缂傚倸鍊哥粔鎾箠濮椻偓瀵偄顓奸崨顖涙畷闂侀€炲苯澧悡銈夋煕瑜庨〃鍛不閹惰姤鐓忓璺虹墕婵¤法绱撻崼婵愮吋闁?Type 11 闂傚倷绀侀幉锛勫垝瀹€鍕剶闁绘挸鍑介懓鍧楁煥濞戞ê顏ら柛瀣崌瀹曠兘顢橀悙鐗堝煕婵?X, Y, Z
                left_node_id = f"{node_id_base(hid)}10"
                _register_node(left_node_id, L, "F", str(hid), 0)

            _remember_member("F", str(hid), left_node_id, _sym1_partner(left_node_id), L, R)
            ganjian.append({
                "member_id": str(hid), "node1_id": left_node_id,
                "node2_id": _sym1_partner(left_node_id), "symmetry_type": 2
            })

        # === 3) 闂傚倷绀侀幉锟犳偡閵夆晛鍌ㄩ柡宥庡幖閻ら箖鎮规潪鎵Э闁绘梻鈷堥弫鍌炴煕閺囥劌澧柍?===
        def _sym2_partner(nid: str) -> str:
            """闂傚倷绀侀幉锟犲箰閸濄儳鐭撻柟缁㈠枛缁犳牗淇婇妶鍛殜闁稿鎹囧Λ鍐ㄢ槈濞嗘帞顢呴柣?sym_type=2)闂傚倷鐒﹂惇褰掑礉瀹€鈧埀顒佸嚬娴滅偛危閹伴偊鏁婇柦妯侯樈閸ゃ倗绱掗悙顒€鍔ゆい鎴濇嚀閻忔劙姊? 0闂?, 1闂?"""
            _m = {"0": "2", "2": "0", "1": "3", "3": "1"}
            return nid[:-1] + _m[nid[-1]] if nid and nid[-1] in _m else _plus_suffix(nid, +2)

        for rid in sorted(right_horizontal.keys(), key=lambda x: float(x)):
            # seg3d = final_coords_map.get(str(rid))
            seg3d = final_coords_map.get(f"R_{rid}")
            if not seg3d: continue
            Lr, Rr = _sort_lr(*seg3d)
            nid_left_guess = _closest_id(Lr, known_nodes, eps=EPS)
            
            if nid_left_guess:
                left_node_id_r = nid_left_guess
            else:
                # 闂傚倸鍊风欢锟犲礈濞嗘挻鍊舵繝闈涚墛椤洟鏌熺€涙ɑ鍎曢柣鏃傗拡閺佸倿鏌涢弴銊ュ闁逞屽墮椤兘寮诲☉妯锋瀻婵☆垵娅ｆ禒鎾⒑缁嬭法绠查拑杈╃磼閸屾氨啸妞わ附鎸抽弻鈩冩媴鐟欏嫬纾抽梺璇″灠閸熸潙鐣烽悢纰辨晝闁靛繆鍓濋惁锝囩磽閸屾瑧鍔嶉柛鏃€甯炲▎銏ゅΧ閸ヮ煈娼熷┑鐘绘涧椤戝懐绱掗埡鍛拺妞ゆ劧绲块‖鑲╃磼閳?30
                left_node_id_r = f"{node_id_base(rid)}30"
                _register_node(left_node_id_r, Lr, "R", str(rid), 0)
            # if nid_left_guess:
            #     left_node_id_r = nid_left_guess
            # else:
            #     # 闂傚倷绶氬褍螞濞嗘挸绀夐柡鍥ュ灩閻鎲搁弮鍫濊摕闁靛ň鏅╅弫濠勭磽娴ｅ顏勵嚕閹稿海绡€闁靛骏绲剧涵鍓х磼婢跺﹦鍩ｇ€规洘鍨块弫鎰緞婵烆潿鍎甸弻鐔煎箹椤撶偟浠紓浣瑰姈椤ㄥ﹪寮诲☉姗嗘僵妞ゆ巻鍋撴い銊︾懅缁辨帒螖閳ь剟宕愰崸妤€鏋佺€广儱娲ｅ▽顏堟煟閹伴潧澧慨锝咁槹缁?Type 11闂傚倷鐒︾€笛呯矙閹达附鍎旈柣鎾崇瘍濞差亜閿ゆ俊銈傚亾缂佺姵濞婇弻鏇熷緞閸繂濮庨梺鍝勬噺閹倿寮诲☉婊呯杸閻庯綆浜滄慨搴♀攽閻愭彃鎮戞い銊ワ工椤?
            #     left_node_id_r = f"{base_id(rid)}10" 
            #     jiedian.append({"node_id": left_node_id_r, "node_type": 11, "X": round(Lr[0],3), "Y": round(Lr[1],3), "Z": round(Lr[2],3), "symmetry_type": 4})
                if left_node_id_r not in known_nodes:
                    _register_node(left_node_id_r, Lr, "R", str(rid), 0)

            _remember_member("R", str(rid), left_node_id_r, _sym2_partner(left_node_id_r), Lr, Rr)
            ganjian.append({
                "member_id": str(rid), "node1_id": left_node_id_r,
                "node2_id": _sym2_partner(left_node_id_r), "symmetry_type": 1
            })




        # === 4) X 闂傚倷鐒﹂幃鍫曞礉瀹€鍕垫晞闁糕剝顨忛悞浠嬫倶閻愭彃鈷旀い鈺冨厴閹鎷呴崨濠呯缂備焦鍔栭〃濠囧蓟閻旇櫣鐭欐繛鍡欏亾閳诲牆鈹戦悙鐑橈紵闁告鍟块悾宄邦潨閳ь剙鐣烽妸鈺婃晣闁绘劗顣介崑鎾寸節濮橆厾鍘遍梺鍦劋缁诲倹绂嶉悙鐑樼厸濞达綀顫夊畷灞绢殽閻愬樊鍎旀鐐叉喘瀹曟粍鎷呮笟顖浶ラ梻鍌氬€风欢锟犲礈濞嗘挻鍊舵繝闈涱儏閸?front/right 闂備浇宕垫慨鍨娴犲绀夐柟瀛樼箥閻掍粙鏌ｅΔ鈧悧蹇涘煝閺冨牊鐓曟繛鍡楁禋濡茬顭?===
        def _x_node_prefix(view_tag: str, xid: str) -> str:
            # 婵犵數鍎戠徊钘壝洪敂鐐床闁告洦鍨板Ч鏌ユ煃瑜滈崜鐔煎箖瀹勬壋鏋庨煫鍥ㄦ濡偛鈹戦悙鑼憼妞ゎ厼娲ㄥΣ鎰板箳濡も偓缁狙囨煙鐎涙绠ラ柛鐐存そ濮婃椽骞愭惔锝傛闂佹椿鍘奸崐鍦偓闈涖偢閸╋繝宕ㄩ鐙€妲柣搴＄畭閸庨亶骞婃惔顭?闂傚倷绀侀幉锟犳偡閵夆晜鍋柛銉墾缂嶆牠鎮楅敐搴℃灈閻熸瑱绠撻幃姗€鎮欑捄杞版睏濡炪倕绻愬畷顒勫煡?xid 婵犵數鍋涢悺銊х尵閸岀偛宸濇い鏃囧Г椤忕喖姊绘担鍝勫姦闁哄懏绻堥垾锕傚醇閵夈儳鐣洪梺鐟板⒔缁垶宕靛澶嬬厱閻忕偛澧介惌濠偯归悪鈧崹鍫曞蓟濞戙垹绠荤€规洖娉﹂妶鍥╃＜?
            return f"{view_tag}{str(xid).replace('_', '')}"

        def _register_x_node(
            preferred_id: str,
            pt: Point3D,
            view_tag: str,
            member_id: str,
            endpoint_index: int,
        ) -> str:
            reuse_id = _closest_id(pt, known_nodes, eps=EPS)
            if reuse_id:
                return reuse_id
            node_id = preferred_id
            if node_id in known_nodes:
                base = preferred_id[:-2] if len(preferred_id) >= 2 else preferred_id
                suffix = preferred_id[-2:] if len(preferred_id) >= 2 else "10"
                idx = 1
                while f"{base}{suffix}{idx}" in known_nodes:
                    idx += 1
                node_id = f"{base}{suffix}{idx}"
            _register_node(node_id, pt, view_tag, str(member_id), endpoint_index)
            return node_id

        def _emit_x_member(view_tag: str, xid: str, seg3d: List[Point3D]):
            if not seg3d or len(seg3d) < 2:
                return
            ordered = sorted(
                ((seg3d[0], 0), (seg3d[1], 1)),
                key=lambda item: (item[0][0], item[0][1]),
            )
            (p1, idx1), (p2, idx2) = ordered
            node1 = _register_x_node(f"{_x_node_prefix(view_tag, xid)}10", p1, view_tag, xid, idx1)
            node2 = _register_x_node(f"{_x_node_prefix(view_tag, xid)}20", p2, view_tag, xid, idx2)
            _remember_member(view_tag, str(xid), node1, node2, p1, p2)
            # 闂傚倷绀侀幉锟犳嚌閻愵剛闄勯柡鍐ㄥ€婚崡姘舵倵濞戞瑯鐒介柍?xid 闂?front/right 婵犵數鍋為崹鍫曞箰閸洖纾归柟鍓х帛閻撳倹绻濇繝鍌滃妞ゃ儱鐗撻弻鏇＄疀閺囩倫銏ゆ煛娴ｅ摜鍩ｉ柡灞剧洴楠炴帡骞嬮悜鍡橆棧闂備胶纭堕弲娑樜涘┑瀣畺濞寸姴顑嗛崑鍕磼鐎ｎ厽纭跺ù婊愮秮濮婅櫣绱掑Ο鍏煎櫧闂佸憡鎸婚惄顖炲箖闂堟稈妲堥柕蹇曞Х妤犲洭姊虹化鏇炲⒉婵炲弶锕㈤、鏇熺鐎ｎ偆鍙嗗┑鐐村灦閿曗晠宕壕淇禸er_id 婵犵數鍋為崹璺侯潖婵犳艾绐楅幖杈剧导閻掑﹥銇勯弽顐粶缂佲偓閸℃稒鐓曢柍鈺佸枤濞堟鐥?
            member_id = str(xid)

            # 濠电姵顔栭崰妤冩崲閹邦喚绀婂ù锝呭閻掍粙鏌ｈ閸婃繈寮婚埄鍐ㄧ窞濠电姴鍠氬Λ娑樷攽閻愬弶顥撻柛銊ㄦ缁骞掑Δ鈧婵囥亜閹捐泛鍓遍柡瀣у亾闂傚倷绀侀幉锟犳嚌閻愵剦娈介柟闂寸贰閺佸銇勯弬鍨挃闁?2)闂傚倷鐒︾€笛呯矙閹寸偟闄勯柡鍐ㄧ墕閻ら箖鏌涢锝嗙妞ゃ儱鐗婇妵鍕閵堝洨鏆悗娈垮枛閻栫厧鐣烽柆宥呭嵆闁绘洑绀佹禒鍝勨攽閻愬樊鍤熷┑顔芥尦楠炲﹥鎯旈姀鈶╂灆闂婎偄娲︾粙鎴︽儗濡ゅ懏鐓曢柟閭﹀墯閳绘洟鏌涢妶鍥ョ紒?1)
            sym_type = 2 if view_tag == "F" else 1

            ganjian.append({
                "member_id": str(member_id),
                "node1_id": node1,
                "node2_id": node2,
                "symmetry_type": sym_type,
            })

        tier_order = {"tier1": 0, "tier2": 1, "tier3": 2}

        def _x_sort_key(view_tag: str, xid: str):
            return (tier_order.get(_tier_for(view_tag, str(xid)), 9), str(xid))

        for xid in sorted(front_x.keys(), key=lambda value: _x_sort_key("F", str(value))):
            fseg = final_coords_map.get(f"F_{xid}")
            if fseg and len(fseg) >= 2:
                _emit_x_member("F", str(xid), fseg)

        for xid in sorted(right_x.keys(), key=lambda value: _x_sort_key("R", str(value))):
            rseg = final_coords_map.get(f"R_{xid}")
            if rseg and len(rseg) >= 2:
                _emit_x_member("R", str(xid), rseg)

        # 闂傚倷鑳堕幊鎾诲床閺屻儱瑙﹂悗锝庡墯閺嗘粓鏌熺紒銏犳灈闁哄绶氶弻锝呂旈埀顒勬偋閸℃瑧鐭?
        pinjie = _build_pinjie_from_front_horiz(final_coords_map, all_models_data, ganjian)
        
    return ganjian, jiedian, pinjie





# I/O
def drop_vertical_members(
    members: CoordDict,
    span_length: Optional[float],
    dx_ratio: float = 0.01,   # 闂傚倷鑳堕崕鐢稿疾濠靛鈧箓宕奸妷顔芥櫔濡炪倖娲嶉崑鎾存叏婵犲倶鍋㈢€规洜鍘ч埞鎴﹀礃閵娿倕顥氱紓浣鸿檸閸欏啴藟閹惧墎鐜绘俊銈呮噺閻撴洘淇婇妶鍛殭闁宠鐗撻弻鏇㈠幢濡ゅ浼愰柧浼欑稻閵囧嫯绠涢幘璺侯杸濠殿噯绲鹃崝娆撶嵁閺嶃劍缍囬柟顖嗗本鍠樻繝?1%
    dx_abs: float = 4.0,      # 缂傚倸鍊搁崐鐑芥倿閿旂偓宕查柛宀€鍎愰弫瀣亜閺囨浜惧┑顔硷工閵堢鐣烽悡搴樻斀闁告劑鍔嬫竟鏇犵磼缂併垹寮い銉︽尵缁絽螖閸涱喚鍘电紓浣割儐椤戞瑥危妞嬪海纾界€广儱妫撮懓璺ㄢ偓瑙勬礃閹倿鐛崶顒夋晣闁绘灏欐导鍥⒒閸屾瑧鍔嶇憸鏉垮暟閹广垽骞掗弮鍌滎槱婵炴潙鍚嬪娆撴儗濡や降浜滈柡宥冨妿缁犳ɑ绻涢崼婵堝煟闁哄被鍔岄埥澶娢熼悡搴毇婵?2~6闂?
    min_len: float = 5.0,     # 闂傚倷鐒﹀鍧楀矗鎼淬劌鍌ㄥΔ锝呭暙閸氬綊骞栧ǎ顒€鐏柍缁樻⒒閳ь剙绠嶉崕閬嶆偋韫囨洜涓嶉柡宥冨妿缁♀偓婵犵數鍋涢悘婵嬪焵椤戭剙鎳忛～鏇熺節闂堟侗鍎愰柣鎺戙偢閺屾盯鈥﹂幋婵囩亪闁汇埄鍨辨繛濠囧蓟閳╁啯濯撮悷娆忓閸戯繝姊洪柅鐐茶嫰婢ь噣鏌涘顒夊剱闁逛究鍔戝畷濂稿Ψ閵壯屾Х?
    return_excluded: bool = False,
):
    """
    婵犵數鍋涢顓熸叏閹绢喖绠犻煫鍥ㄦ磵閸嬫捇宕归銈囩厐濡炪値鍋呯换鍫濐嚕閸洖绠ｉ柨鏃囨閻ㄦ椽姊绘担渚敯闁糕晜鐗曠叅闁哄秲鍔庨梽?闂備礁澧界划顖氼焽?闂傚倷绀侀幉锛勬暜閸ヮ剙纾归柡鍥ュ灪閸嬧晛螖閿濆懎鏆欓柣蹇氭珪缁绘繃绻濋崒娑辨￥缂備胶濯崰姘辨閹烘绫嶉柍褜鍓熼幃褍顭ㄩ崗鐘虫そ瀹曠螖閳ь剟鎮橀搹顐ょ瘈闁割煈鍋呯亸鐢电磼閳ь剚寰勬繛?X 闂傚倷鑳堕…鍫ユ晝閵夆晜鍋￠柍鍝勬噹閻掑灚銇勯幒鍡椾壕濡炪倧瀵岄崳锝夊箠濞嗘挸绠ｉ柨鏇楀亾缂佲偓閸儲鐓涢柛鎰╁妿婢ф盯鏌ｅ┑鍫濇灈闁?
        缂傚倸鍊烽悞锕€顫忚ぐ鎺撳亱婵犲﹤鍘惧ú顏勯敜婵°倐鍋撶紒鈧崱娑欑厪闁割偅绻冮崳浠嬫煛閸℃洖宓嗛柡灞诲妼閳藉鈻庨幋鐐寸暦闂備礁澧界划顖氼焽缁?<= max(dx_abs, dx_ratio * span_length)
    - span_length: 闂傚倷绀侀幉锟犳偡閵夆晛纾瑰ù鐘差儏閻掑灚銇勯幒鍡椾壕闂佸摜鍣ラ崑濠傤嚕娴兼潙纾兼繛鎴炵懃閸斿懘姊洪幐搴㈩梿闁稿鍔楃划鍫ュ礋椤撴稑浜鹃柣鎰嚀閳ь剚绻勭槐鎾愁潩妫版繃鏅╅梺鍛婄☉閻°劑宕戦妸鈺傜厪濠电偟鍋撻弶娲煃瑜滈崜娆撴晝閵堝牏浜芥俊鐐€曠换鎰板箠韫囨洜绀婇柛鏇ㄥ灡閳锋帡鏌嶈閸撶喎鐣疯ぐ鎺濇晩缁炬澘宕弫?seg_len闂傚倷鐒︾€笛呯矙閹次层劑鍩€椤掑倻纾奸弶鍫氭櫆缁€濯渘e 闂傚倷绀侀幖顐﹀疮閸愭祴鏋栨繛鎴炲殠娴滃湱鎲搁弮鍫濈畺?dx_abs闂?
    - min_len: 缂傚倸鍊烽懗鍫曞磻閹惧灈鍋撶粭娑樻祩閺佸﹦鈧厜鍋撻柛鏇ㄥ亞閻ｈ鲸绻濋悽闈浶ｇ痪鏉跨Т琚?< min_len 婵犵數鍋為崹鍫曞箰閸濄儳鐭撻柟缁㈠枛閸ㄥ倿鏌ｉ敐鍛伇闁告宀搁弻鈥愁吋鎼粹€茬凹缂備胶铏庨崹鍫曞蓟閵娿儮妲堟俊顖濆亹娴煎洤鈹戦悙鏉戠祷婵炵》绻濋悰顕€骞掑Δ鈧敮闂侀潧鐗嗗ú銊╊敊閺冨牊鈷戝ù鍏肩懅缁嬪鏌ｉ悤鍌滅М闁糕斁鍋?
    闂備礁鎼ˇ顐﹀疾濠婂牆钃熼柕濞垮剭濞差亜鍐€妞ゆ挾鍠愬▍鏍р攽椤旀枻渚涢柛瀣缁粯绂掔€ｎ偆鍘介梺鎸庣箓濡盯骞婇崘顔界厽闁愁垱鐟ュú銈囩矆閸岀偞鈷掗柛顐ｇ濞呭洨绱掗埀顒佸緞閹邦厾鍘?(婵犵數鍎戠徊钘壝洪敂鐐床闁告洦鍨板Ч鏌ユ煃? 闂備浇宕甸崑鐐哄礄瑜版帒纾婚柛鏇ㄥ墯濞呯姷鎲搁弬娆炬綎?闂傚倷鐒︾€笛呯矙閹达附鍋嬮柛鈩冪懅缁€?return_excluded=True闂?
    """
    dx_th = float(dx_abs)
    if span_length is not None:
        dx_th = max(dx_th, float(dx_ratio) * float(span_length))

    kept: CoordDict = {}
    excluded: CoordDict = {}

    for k, seg in members.items():
        if not seg or len(seg) < 2:
            kept[str(k)] = seg
            continue
        (x1, y1), (x2, y2) = seg
        dx = abs(float(x2) - float(x1))
        dy = abs(float(y2) - float(y1))
        L  = math.hypot(dx, dy)
        if L < float(min_len):
            kept[str(k)] = seg
            continue
        if dx <= dx_th:
            excluded[str(k)] = seg
        else:
            kept[str(k)] = seg

    return (kept, excluded) if return_excluded else kept


# ====== New: Vertical stacking alias builder & post-processor ======
from typing import Set

def build_vertical_reuse_aliases(final_coords_map: Dict[str, List[Point3D]],
                                 all_models_data: Dict[str, dict],
                                 eps: float = 1e-6) -> Dict[str, str]:
    """
    闂傚倷绀侀幖顐︻敄閸涱垪鍋撳鐓庡缂佽鲸鎹囬獮妯兼嫚閼碱兛绱滄繝鐢靛Т鑹岄柛瀣尵缁辨帒螖閳ь剟宕愰崷顓犵煓濠㈣泛澶囬崑鎾绘晲鎼粹€愁潽缂備椒鐒﹂悡鈥愁潖濞差亶鏁囬柣鎴濇閸氬姊虹粙鍧楊€楅柣掳鍔庣划瀣箳閺冣偓瀹曞鏌ц箛鏇熷殌闁轰降鍊濆娲川婵犲倻浠村┑鈽嗗亝閻熲晛顕ｉ锔绘晪闁逞屽墴閻涱喖顫滈埀顒勭嵁鐎ｎ喗鍋戦柍褜鍓氱€靛ジ宕掗悙瀵稿幗闂佸綊鍋婇崰妤呭吹閳ь剙顪冮妶蹇涙闁绘搫绻濋獮鍐╃鐎ｎ€晠鏌嶉崹娑欐珔濞存粎鍋撶换婵嬫濞戞艾顤€闂佷紮缍佹禍鍫曞蓟濞戙垹绠虫繝闈涙缁ㄥ姊虹拠鈥虫灍婵炲弶绮撻獮鍐╁缁厜鍋撻敃鍌氱闁哄啫鍊诲畷?
      - 闂?婵犵數鍋為崹鍫曞箰閹间焦鏅濇い蹇撶墕绾惧潡鎮楀☉娆樼劷妞?闂傚倷鑳剁涵鍫曞疾濞戙垹绠规い鎰剁畱闂傤垱銇勯弽顐粶缂備讲鏅滈妵鍕冀閵娧€濮囬柣搴㈡皑閸樠囧煡婢舵劕绠婚柟棰佺閸撳啿顪冮妶鍛闁告挾鍠栭獮?sid20) 婵?婵犵數鍋為崹鍫曞箰閹间緡鏁勫鑸靛姇绾惧潡鎮楀☉娆樼劷妞?闂傚倷鑳剁涵鍫曞疾濞戙垹绠规い鎰剁畱闂傤垱銇勯弽顐粶缂備讲鏅滈妵鍕冀閵娧€濮囬柣搴㈡皑閸樠囧煡婢舵劕绠荤紒娑氭嚀婵稑顪冮妶鍛闁告挾鍠栭獮?sid10) 闂?D婵犵數鍋為崹鍫曞箹閳哄懎鐭楅柛鎰靛枛闂傤垶鏌熼梻瀵割槮閻?<=eps)闂?
        闂?alias[婵犵數鍋為崹鍫曞箰閹间緡鏁勫鑸靛姇绾惧潡鎮楀☉娆樼劷妞も晠顥撶槐鎺撳緞鐎ｎ剙鐭梔10(+闂備浇顕ч柊锝咁焽瑜嶉敃銏℃綇椤愮喎寰?/2/3)] = 婵犵數鍋為崹鍫曞箰閹间焦鏅濇い蹇撶墕绾惧潡鎮楀☉娆樼劷妞も晠顥撶槐鎺撳緞鐎ｎ剙鐭梔20(+闂備浇顕ч柊锝咁焽瑜嶉敃銏℃綇椤愮喎寰?/2/3)闂?
    婵犵數濮伴崹鐓庘枖濞戞◤娲晝閸屾碍鐎梺缁樺姉閸庛倝寮查浣瑰弿婵妫楁晶浼存煕閻愵亜濮傞柡灞剧洴楠炲鈹戦崶鑸碉紒闂備浇妗ㄧ欢锟犲闯閿濆宓佹慨妞诲亾妤犵偛顑夐弫鍌炴偡妫颁礁顥氬┑鐘灱濞夋盯顢栭崨鎼晜闁靛鏅滈崑鈩冪箾閸℃绠版い蹇婃櫊閺屾盯鈥﹂幋婵堜画缂?generate_outputs 闂備浇顕уù鐑藉箠閹剧粯鍤愭い鏍仜閻鐓崶銊︹拻闁崇粯妫冮弻宥堫檨闁告挾鍠栭獮濠傗槈濞嗘劗绉堕梺鍛婃寙閸涱垰鐐婂┑鐘愁問閸ｎ垳寰婇悾灞惧床閻庯綆鍠楅悡鍌涚節婵犲倻澧涢柣鎺楃畺閺屾洘绻涢崹顔瑰亾閺嶎収鏁冮柤鎭掑劜閸欏繑绻濋崹顐ｅ暗缂佸鍠楃换娑㈡⒒閺夋垵绁悗娈垮枔閸旀垿銆佸☉妯锋婵炲棗娴氭导鏍р攽閻愭潙鐏﹂柟灏栨櫊瀹曘垺銈ｉ崘銊э紱濡炪們鍊楅崑銈夊蓟閿熺姴閱囨慨姗嗗厸婢规洟姊虹拠鑼缂佺粯鍔楅幑銏犖旈崨顓犲姦濡炪倖宸婚崑鎾绘煙閸愯尙鐒搁柛鈹惧亾?
    """
    parts = []
    # 闂傚倷鑳堕幊鎾诲箟閿熺姴鍨傞柣銏㈩焾閸氳銇勯幘璺衡偓顐﹀箳閺囩姷鏉搁柟鍏肩暘閸斿苯鈻撳┑瀣拻濞撴艾娲ら弸鏃堟煕閺傛鍎忛柍璇查叄婵偓闁靛牆妫楅崜顓㈡⒑閸涘﹥纾搁柛鏂款樀瀹曟垿骞橀幇浣哄弳闂佸憡鍔︽禍婊堝极閵堝鈷戦柛娑橈工閻忋儲淇婇锝囨噰鐎殿噮鍋婇、姘跺焵椤掑嫮宓佹慨妞诲亾妤犵偛顑夊顒勫传閸曨亜顥氭繝鐢靛█濞佳囧箠瀹ュ洩濮冲ù鐓庣摠閻撴洘绻涢崱妤呯崪婵﹥顨堢槐鎺懳旈埀顒勫磹閸︻厾鐭欏璺哄閸嬫捇鏁愭惔鈥斥拻婵炲鍘ч崐鍧楀蓟閿濆绠涙い鏃囨濞堝苯鈹戦悙鎻掓倯妞ゃ劌锕ら?
    for stem, pack in (all_models_data or {}).items():
        args = (pack or {}).get("ganjian_args", {}) or {}
        front_support: Dict[str, list] = {str(k): v for k, v in (args.get("front_support") or {}).items()}
        base_sid, min_cx = None, None
        for sid in sorted(front_support.keys(), key=lambda x: float(x)):
            # seg3d = final_coords_map.get(str(sid))
            seg3d = final_coords_map.get(f"F_{sid}")

            if not seg3d or len(seg3d) < 2:
                continue
            cx = 0.5 * (float(seg3d[0][0]) + float(seg3d[1][0]))
            if (min_cx is None) or (cx < min_cx):
                min_cx, base_sid = cx, str(sid)
        if not base_sid:
            continue
        # pA, pB = final_coords_map[base_sid]
        pA, pB = final_coords_map[f"F_{base_sid}"]
        topP, botP = _top_bottom(pA, pB)  # z 闂備浇顕х换鎰崲閹邦喗宕叉俊銈呮噹閻掑灚銇勯幒鍡椾壕闂佺懓鍟跨粔鍫曞箯瑜版帗鍋勯柛婵勫劗閺嬫牗绻濋悽闈浶㈤悗姘舵敱鐎?
        parts.append({"stem": stem, "sid": base_sid, "top": topP, "bot": botP})

    aliases: Dict[str, str] = {}
    # 婵犵數鍋為崹鍫曞箰閸洖纾归柟鎹愬煐閸嬫牠鏌涘Δ鍐ㄢ偓锝呪槈閵忕姷鍔﹀銈嗗笒鐎氼剟鎷戦悢鍏肩厪濠㈣埖锚閻忥絿绱掗幇顓ф當闁宠棄顦甸獮妯肩驳绾懎鎯堥梻浣侯焾妤犳悂鎮洪妸褏鐭夐柟鐑橆殔缁€鍫澝归敐鍛础闁?bot 婵?婵犵數鍋為崹鍫曞箰閹间緡鏁勫鑸靛姇绾惧潡鎮楀☉娆樼劷妞も晝鍏橀弻娑㈠箻閼碱剙濡介梺?top 闂傚倷绀侀崥瀣儑瑜版帒纾块柣銏㈩焾闂傤垶鏌熼梻瀵割槮閻熸瑱绠撻弻娑㈩敃椤愩垹顫紓浣插亾濠㈣埖鍔栭悡鏇㈡煙閻戞ɑ灏甸柟鍐叉噺缁绘盯宕ㄩ銏犲Б闂?alias(婵犵數鍋為崹鍫曞箰閹间焦鍋橀柣顏勭┍10 -> 婵犵數鍋為崹鍫曞箰閹间降鈧懐绮甸惂?0)
    for i in range(len(parts)):
        upper = parts[i]
        for j in range(len(parts)):
            if i == j: 
                continue
            lower = parts[j]
            if _dist3(upper["bot"], lower["top"]) <= float(eps):
                lower_sid10 = f"{lower['sid']}10"
                upper_sid20 = f"{upper['sid']}20"
                # 闂傚倷绀侀幉锟犫€﹂崶顒€绐楅幖鎼厜缂嶆牠鏌熼幍顔碱暭闁?
                aliases[lower_sid10] = upper_sid20
                # 闂備浇顕ч柊锝咁焽瑜嶉敃銏℃綇椤愮喎寰旈梻?(+1/+2/+3)
                aliases[_plus_suffix(lower_sid10, +1)] = _plus_suffix(upper_sid20, +1)
                aliases[_plus_suffix(lower_sid10, +2)] = _plus_suffix(upper_sid20, +2)
                aliases[_plus_suffix(lower_sid10, +3)] = _plus_suffix(upper_sid20, +3)
    return aliases


def apply_id_aliases(ganjian: list, jiedian: list, pinjie: list, id_aliases: Dict[str, str]):
    """
    闂備浇顕уù鐑藉极婵犳艾鐒垫い鎺嶈兌閵嗘帡鏌ｉ悢椋庣闁逞屽墯椤旀牠宕板顓熷弿濡わ絽鍟繚闂佸憡鍔忛弲婊勭閵堝棛绠鹃柟瀵稿仧閻倝鏌￠埀?ID 濠电姵顔栭崰妤冩崲閹邦喖绶ゅù鐘差儏缁犳牠鏌￠崶銉ョ仼缂佲偓瀹€鍕厸鐎广儱娲﹂弳鈺冪磼閳ь剟宕熼娑氬幈闂佸湱鍎ょ换鍌涚濠婂牊鐓欐い鏃囧Г缁€瀣偓娈垮枟閹告娊鐛幇顓熷劅闁炽儱纾崫搴ㄦ⒒娴ｇ懓顕滅紒瀣灴绡撻柍褜鍓涚槐鎺撴綇閵娧呯杽闂佺粯渚楅崰姘跺箲閸曨剚濮滈柟娈垮櫍閳瑰繘姊绘繝搴′簻婵炲眰鍊濋獮濠囧箻濮瑰洠鍋撻崨瀛樻櫇闁稿本绋戦崜顓㈡⒑閸涘﹥澶勯柛瀣缁鎮介崨濞炬嫼闂佸湱绮敮鐐哄煝瀹€鈧槐?
      - ganjian: 闂傚倷绀侀幖顐⒚洪敂閿亾缁楁稑鍟伴弳?node1_id/node2_id闂傚倷鐒︾€笛呯矙閹达附鍤愭い鏍仧瀹撲線鏌熼崜褏甯涢柣鎾冲€婚埀顒€绠嶉崕鍗灻洪敂鍓х焾闁哄被鍎查悡鏇熸叏濮楀棗澧伴柣鎺楁敱閵囧嫰寮幐搴ｂ敍闂?
      - jiedian: 
          * 11缂傚倸鍊风欢锟犲磻閸屾粍顫曟い鏃傚亾椤洖霉閸忓吋缍戦悷娆欑畵閹﹢鎮欑捄杞版睏濡?node_id 闂傚倷绀侀幉锟犳偡椤栨稓顩叉繛鍡樺灦瀹曞弶鎱ㄥΟ鍨厫闁稿鏅滅换娑㈠幢濡や焦宕冲銈呯箻娴滃爼寮婚埄鍐ㄧ窞闁糕剝锕╁鎰磽娓氣偓娴滆埖绂嶉崼鏇炵疇?node_id 闂備浇宕甸崑鐐哄礄瑜版帒纾婚柛娑卞帣閿濆牜妲炬繛瀛樼矋閹倸鐣烽悢纰辨晝闁靛繈鍨圭敮鎾绘⒒娴ｄ警鐒剧紒缁樺灥閿曘垽宕烽鐐茬亰闂佽崵鍋樼粭宥夋⒒娴ｇ懓顕滅紒瀣灴閹崇喖顢涢悙鎻掔€銈嗙墬缁嬫帞绱為崶顒佺厵闁诡垎鍐╂瘣濠殿噯绲介ˇ鐢稿蓟瀹ュ唯闁挎柨澧介悡浣割渻閵堝棗绗氱紒顔芥尭閻ｇ兘濡烽妷顔兼倯婵炶揪绲捐ぐ鍐╃閻愵剛绡€濠电姴瀚﹢浠嬫⒒娴ｇ懓顕滅紒瀣灦缁轰粙寮惔鎾搭潔濡炪倕绻愮€氱兘宕甸弴銏＄厱闁规壋鏅涙俊濂告煟閹烘垯鍋㈤柡灞剧☉椤繈顢栫捄銊ф喒D
          * 12缂傚倸鍊风欢锟犲磻閸屾粍顫曟い鏃傚亾椤洟鏌ｉ妸銏犱壕ode_id 闂傚倷绀侀幉锟犳偡閵夆晜鏅濋柕鍫濐槸閻?X/Y 闂傚倷绀侀幉锟犳偡閵夆晛纾瑰ù鐘差儏閻掑灚銇勯幒鍡椾壕闂佺瀛╅埀顒佸姍濮婄粯绗熼崶褎鐏曞┑鈽嗗亜鐎氼厾绮嬮幒鎴旀闁靛繒濮烽ˇ顐㈩渻閵堝棗濮傞柛銊︽そ瀹曟劙骞庨懞銉у幐闂佹悶鍎崝宀勵敋濠婂應鍋撶憴鍕闁绘搫绻濆顐㈩吋閸涱亝顫嶅┑鈽嗗灥椤曆囧焵椤掆偓瀹曨剟鍩ユ径鎰妞ゆ牗鐭竟?node_id 闂傚倷绀侀幉锟犳偡椤栨稓顩叉繛鍡樺灦瀹曞弶鎱ㄥΟ鍨厫闁稿鏅滅换娑㈠幢濡や焦宕冲銈呯箻娴滃爼寮?
      - pinjie: node_id 闂傚倷鑳堕…鍫ヮ敄閸℃稒鍤屽Δ锝呭暙閺勩儵鏌涢埄鍐槈閻熸瑱濡囬埀顒€绠嶉崕鍗炍涘▎鎴犵焿鐎光偓閸曨剛鍘甸柣鐘叉礌閸撴繄娆㈠☉姘辩＜閺夊牄鍔庣粻鐐碘偓瑙勬磸閸ㄨ櫣鎹㈠┑鍡╂僵妞ゆ帊绶℃禒褔姊绘担鐟邦嚋缂佸鍨块幃褔宕ㄩ娑樺簥濠殿喗顭堥崺鏍磻閳哄倻绠鹃柛鈩兠悞楣冩煕鎼淬垹鐏ラ柍钘夘樀楠炴﹢顢涘顐㈩棜濠电姷鏁搁崑娑樜涚仦杞匡綁宕熼鐕佹綗?
    """
    def canon(value: str) -> str:
        """
        闂備浇顕х换鎰崲閹邦儵娑㈠籍閸繄顔夐梺闈涚箞閸婃洜绮诲☉銏㈠彄闁搞儯鍔忔竟姗€鎽堕敓鐘斥拺?闂佽瀛╅鏍窗濡も偓鐓ゆ繝濠傜墕閺?ID 闂備浇宕甸崰鎰版偡閵壯€鍋撳鐓庡籍鐎殿喗濞婇弫鎰緞婵犲嫷妲撮梻浣虹帛椤ㄥ懘鎮ф繝鍐浄婵☆垵鍋愮壕钘壝归敐鍛喐濠⒀勬礋閺岋綁寮崫鍕闂?ID闂?
        闂傚倷娴囬妴鈧柛瀣尰閵囧嫰寮介妸褉妲堥梺浼欏瘜閸ｏ綁骞冩禒瀣垫晬闁靛牆顦伴宥呪攽閻橆偄浜炬繛鎾村焹閸嬫挾鈧娲樼划宀勵敇婵傜鐐婇柍鍝勫枦缁?'1' 闂傚倷鐒﹂惇褰掑礉瀹€鈧埀顒佸嚬閸撴稑危閹版澘鐓涢柛娑卞枛娴犳椽姊洪棃娑辩劸闁稿孩鎸冲畷鍝勭暆閳ь剟鍩€椤掍緡鍟忛柛鐘崇墬椤ㄣ儴绠涢弴鐕佹綗闂佺粯顨呴悧鍡涱敋鏉堛劍鍙忔慨妤€妫楁晶顕€鎮介妯哄姦闁诡喖鍢查埢搴♀枎閹寸姁鎴︽⒑鐠囪尙鍑圭紒顔界懃閻ｅ嘲顭ㄩ崘鎯ф倯闂佹悶鍎弲婵嬫晬濞戙垺鈷戦柛娑橈龚婢规﹢姊虹敮顔惧埌妞ゎ厼娲︾€佃偐鈧稒锚閸擃參姊洪崨濠冨闁告ü绮欏畷娲磼閻愭潙鈧?ID闂?
        闂備浇顕уù鐑藉箠閹捐瀚夋い鎺戝閸ㄥ倹鎱ㄥΟ鎸庣【缂佲偓閸℃ǜ浜滈柟鎵虫櫅閻忣亪鏌涙繝鍐ㄢ枙闁哄瞼鍠栭幊婊冾嚗濡ゅ﹣娴烽柕鍥ㄥ姍瀵噣宕煎┑濞︽洟鏌熼懖鈺勊夐柍褜鍓濆▍鏇炩枍閸愵喗鈷戦悹鍥ｂ偓鍐茬闂佹悶鍔岀紞濠呮闂佸搫琚崕閬嶅磼閵娾晜鐓熼柡鍌氱仢椤ュ繘鏌涢弬鍨殻闁哄本鐩獮妯虹暦閸ュ棎鍊楃槐鎺撴綇閵娿儳浼屾繝?
        """
        def _lift(one: str) -> str:
            seen: Set[str] = set()
            cur = one
            while cur in id_aliases and cur not in seen:
                seen.add(cur)
                cur = id_aliases[cur]
            return cur

        s = str(value)
        # 闂備礁鎼ˇ顐﹀疾閳哄懎鍌ㄦ繛宸簻閼歌銇勯幒鎴濐仾闁稿骸閰ｉ弻鈩冨緞鐎ｎ亞浠撮梺缁樻尭閸婂潡寮婚敓鐘茬劦妞ゆ帒瀚崵瀣煕椤垵浜濋柣锝勫嵆濮婃椽骞愭惔锝傛闂佹椿鍘奸崐鍦偓闈涖偢閸╋繝宕ㄩ鐙€妲柣搴＄畭閸庨亶藝娴兼潙绠犻柣妯碱暯閸嬫挸鈻撻崹顔界亪缂備胶绮崹闈涘祫閻熸粌绻戠粋宥夊箹娴ｅ摜顦板銈嗗坊閸嬫捇鏌ｈ箛鏃戞疁闁哄本鐩獮妯虹暦閸ュ棎鍊楃槐鎺撴綇閵娿儳浼岄悗娈垮枟閹告娊鐛幇顓熷劅闁炽儱纾崫搴ㄦ⒒娴ｅ憡鍟為柤鐟板⒔閼洪亶鎳栭埡浣哥亰濠电偞鍨崹褰掓儗濡や降浜滈柡宥冨妿閻鏌涢埡鍌溿€掔紒杈ㄦ尰缁楃喖宕惰缁犺崵绱撴担闈涘婵炲娲滈崚鎺撶節濮橆剛鍔?
        while True:
            direct = _lift(s)
            if direct != s:
                s = direct
                continue

            if s.startswith("1") and len(s) > 1:
                tail = s[1:]
                canon_tail = _lift(tail)
                if canon_tail != tail:
                    s = "1" + canon_tail
                    continue
            break
        return s

    # ---- ganjian ----
    new_g = []
    seen_g = set()
    for row in (ganjian or []):
        r = dict(row)
        r["member_id"] = str(r.get("member_id"))
        r["node1_id"] = canon(str(r.get("node1_id")))
        r["node2_id"] = canon(str(r.get("node2_id")))
        key = (r["member_id"], r["node1_id"], r["node2_id"], r.get("symmetry_type"))
        if key in seen_g:
            continue
        seen_g.add(key)
        new_g.append(r)

    # ---- jiedian ----
    new_j = []
    seen_j = set()
    for row in (jiedian or []):
        r = dict(row)
        nid = canon(str(r.get("node_id")))
        r["node_id"] = nid
        if r.get("node_type") == 12:
            if "X" in r: r["X"] = canon(str(r["X"]))
            if "Y" in r: r["Y"] = canon(str(r["Y"]))
            if "Z" in r and isinstance(r.get("Z"), str): r["Z"] = canon(str(r["Z"]))
            key = ("12", nid)
            if key in seen_j: 
                continue
            seen_j.add(key)
            new_j.append(r)
        else:  # 11 闂傚倷鑳堕幊鎾绘偤閵娾晜鍋嬮柡鍥ュ灩閻鏌涢幘妞诲亾闁?
            key = ("11", nid)
            if key in seen_j:
                continue
            seen_j.add(key)
            new_j.append(r)

    # ---- pinjie ----
    new_p_items = []
    seen_p = set()
    for item in (pinjie or []):
        if not isinstance(item, list) or not item:
            continue
        nid = canon(str(item[0]))
        if nid in seen_p:
            continue
        seen_p.add(nid)
        coord = item[1] if len(item) > 1 else None
        new_p_items.append([nid, coord])

    return new_g, new_j, new_p_items
