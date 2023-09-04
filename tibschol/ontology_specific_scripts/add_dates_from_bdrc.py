from apis_ontology.models import Person
from tqdm.auto import tqdm
import logging
from datetime import date

LIFESPANS = {
    "P753": {"end_date": "1055", "start_date": "0958"},
    "P2551": {"start_date": "1059", "end_date": "1109"},
    "P3389": {"start_start_date": "0900", "start_end_date": "0999"},
    "P3143": {"end_start_date": "1128", "end_end_date": "1198", "start_date": "1016"},
    "P2614": {"start_start_date": "1000", "start_end_date": "1099"},
    "P4920": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3822": {"start_start_date": "1000", "start_end_date": "1099"},
    "P4457": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3465": {"start_start_date": "1000", "start_end_date": "1099"},
    "P2274": {"start_start_date": "1000", "start_end_date": "1099"},
    "P4633": {"start_date": "1077", "end_date": "1161"},
    "P5746": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3975": {"start_start_date": "1000", "start_end_date": "1099"},
    "P2552": {"start_start_date": "1000", "start_end_date": "1099"},
    "P2273": {"end_date": "1174", "start_date": "1100"},
    "P52": {"start_start_date": "1000", "start_end_date": "1099"},
    "P8LS15289": {"end_date": "1143", "start_date": "1075"},
    "P1316": {"end_date": "1118", "start_date": "1042"},
    "P3379": {
        "start_start_date": "0972",
        "start_end_date": "0982",
        "end_start_date": "1054",
        "end_end_date": "1055",
    },
    "P2557": {"start_start_date": "1004", "start_end_date": "1005", "end_date": "1064"},
    "P3466": {"start_date": "1023", "end_date": "1115"},
    "P3442": {"start_date": "1027", "end_date": "1105"},
    "P3473": {"start_date": "1038", "end_date": "1103"},
    "P1404": {"end_date": "1169", "start_date": "1109"},
    "P4749": {"start_start_date": "1000", "start_end_date": "1099"},
    "P4669": {"start_date": "1077", "end_start_date": "1156", "end_end_date": "1158"},
    "P2259": {"start_start_date": "1100", "start_end_date": "1199"},
    "P4747": {"start_start_date": "1100", "start_end_date": "1199"},
    "P1982": {"end_date": "1185"},
    "P3089": {"end_date": "1253"},
    "P1618": {"end_date": "1182", "start_date": "1142"},
    "P3785": {"start_start_date": "1100", "start_end_date": "1199"},
    "P1400": {"end_date": "1193", "start_date": "1110"},
    "P127": {"end_date": "1170", "start_date": "1110"},
    "P1827": {"start_start_date": "1300", "start_end_date": "1399"},
    "P3448": {"start_date": "1121", "end_date": "1189"},
    "P3722": {"start_start_date": "1100", "start_end_date": "1199"},
    "P3779": {"start_start_date": "1100", "start_end_date": "1199"},
    "P5651": {"start_date": "1055"},
    "P1405": {"start_date": "1070", "end_date": "1141"},
    "P4455": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3447": {"start_date": "1101", "end_date": "1175"},
    "P4458": {"start_start_date": "1000", "start_end_date": "1099"},
    "P5753": {"start_start_date": "1100", "start_end_date": "1199"},
    "P4007": {"start_date": "1172", "end_date": "1236"},
    "P2271": {"end_date": "1232", "start_date": "1153"},
    "P2582": {"start_start_date": "1200", "start_end_date": "1399"},
    "P2585": {"start_start_date": "1100", "start_end_date": "1199"},
    "P3998": {
        "start_date": "1184",
        "end_date": "1241",
        "start_start_date": "1100",
        "start_end_date": "1199",
    },
    "P1514": {"start_date": "1182", "end_date": "1261"},
    "P1056": {"start_date": "1182", "end_date": "1251"},
    "P63": {"start_start_date": "1200", "start_end_date": "1399"},
    "P66": {"start_date": "1284", "end_date": "1339"},
    "P4312": {"end_date": "1378", "start_date": "1299"},
    "P1413": {"start_date": "1350", "end_date": "1405"},
    "P3645": {"start_date": "1117", "end_date": "1192"},
    "P2375": {"start_start_date": "1100", "start_end_date": "1199"},
    "P858": {"end_date": "1313", "start_date": "1243"},
    "P10599": {"start_start_date": "1200", "start_end_date": "1299"},
    "P3462": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3718": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3475": {"end_date": "1138", "start_date": "1075"},
    "P1226": {"end_date": "1375", "start_date": "1312"},
    "P8LS15353": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3775": {"start_date": "1160", "end_date": "1217"},
    "P4088": {"start_date": "1127", "end_date": "1185"},
    "P3446": {"end_date": "1166", "start_date": "1106"},
    "P8LS15357": {"start_start_date": "1100", "start_end_date": "1199"},
    "P3449": {"start_date": "1158", "end_date": "1232"},
    "P8LS15360": {"start_start_date": "1300", "start_end_date": "1399"},
    "P8LS15363": {"start_start_date": "1400", "start_end_date": "1499"},
    "P3060": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3063": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3064": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3709": {"start_start_date": "1000", "start_end_date": "1099"},
    "P2272": {"start_start_date": "1100", "start_end_date": "1199"},
    "P1319": {"start_start_date": "1100", "start_end_date": "1199"},
    "P136": {"start_start_date": "1100", "start_end_date": "1199"},
    "P1320": {"start_date": "1129", "end_date": "1215"},
    "P3065": {"start_start_date": "1100", "start_end_date": "1199"},
    "P3976": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3485": {
        "end_date": "1210",
        "start_start_date": "1100",
        "start_end_date": "1199",
        "start_date": "1138",
    },
    "P4456": {"end_date": "1194", "start_date": "1122"},
    "P5740": {"start_start_date": "1000", "start_end_date": "1099"},
    "P2640": {"start_date": "1179", "end_date": "1250"},
    "P1060": {"start_date": "1210", "end_date": "1285"},
    "P4252": {"start_date": "1187", "end_date": "1250"},
    "P1355": {"end_date": "1286", "start_date": "1214"},
    "P16": {"start_date": "1143", "end_date": "1217"},
    "P2649": {"end_start_date": "1209", "end_end_date": "1210", "start_date": "1142"},
    "P1217 ": {"start_date": "1227", "end_date": "1305"},
    "P1298": {"end_date": "1375", "start_date": "1299"},
    "P2147": {"start_start_date": "1200", "start_end_date": "1299"},
    "P2639": {"start_start_date": "1200", "start_end_date": "1299"},
    "P1060 ": {"start_date": "1210", "end_date": "1285"},
    "P3642": {"start_start_date": "1100", "start_end_date": "1199"},
    "P1048": {"start_date": "1235", "end_date": "1280"},
    "P4137": {"end_date": "1259", "start_date": "1186"},
    "P3644": {"start_start_date": "1200", "start_end_date": "1299"},
    "P1217": {"start_date": "1227", "end_date": "1305"},
    "P1219": {"start_date": "1219", "end_date": "1299"},
    "P6145": {"start_date": "1271"},
    "P8966": {"end_date": "1475", "start_date": "1372"},
    "P5741": {"start_start_date": "1200", "start_end_date": "1299"},
    "P141": {"start_start_date": "1200", "start_end_date": "1299"},
    "P1303": {"start_date": "1259", "end_date": "1325"},
    "P1830": {"end_date": "1369", "start_date": "1295"},
    "P153": {"start_date": "1299", "end_start_date": "1353", "end_end_date": "1354"},
    "P856": {"end_date": "1527", "start_date": "1441"},
    "P3963": {"start_start_date": "1300", "start_end_date": "1399"},
    "P4921": {"start_start_date": "1300", "start_end_date": "1399"},
    "P6146": {"start_start_date": "1200", "start_end_date": "1299"},
    "P3090": {"start_start_date": "1200", "start_end_date": "1299"},
    "P2085": {"end_date": "1342", "start_date": "1276"},
    "P3445 ": {"end_date": "1123", "start_date": "1054"},
    "P5907": {"start_start_date": "1300", "start_end_date": "1399"},
    "P1840": {"start_date": "1059", "end_date": "1131"},
    "P4872": {"start_date": "1171"},
    "P0RK972": {"start_start_date": "1300", "start_end_date": "1399"},
    "P1943": {"start_start_date": "1300", "start_end_date": "1399"},
    "P58": {"start_date": "1402", "end_date": "1472"},
    "P4271": {"start_date": "1432", "end_date": "1506"},
    "P3357": {"start_start_date": "1300", "start_end_date": "1399"},
    "P5276": {"start_start_date": "1400", "start_end_date": "1499"},
    "P2093": {"end_date": "1445", "start_date": "1383"},
    "P2414": {"end_date": "1401", "start_date": "1319"},
    "P2374": {"end_date": "1294", "start_date": "1212"},
    "P151": {"start_date": "1294", "end_date": "1376"},
    "P144": {"start_start_date": "1200", "start_end_date": "1299"},
    "P2581": {"start_start_date": "1300", "start_end_date": "1399"},
    "P2462": {"start_start_date": "1300", "start_end_date": "1399"},
    "P22": {"start_date": "1719", "end_date": "1794"},
    "P3991": {"start_start_date": "1000", "start_end_date": "1099"},
    "P404": {"end_date": "1116", "start_date": "1032"},
    "P1844": {"end_date": "1153", "start_date": "1079"},
    "P1854": {"start_start_date": "1000", "start_end_date": "1099"},
    "P6472": {"start_start_date": "1100", "start_end_date": "1199"},
    "P1615": {"end_date": "1158", "start_date": "1092"},
    "P139": {"start_date": "1292", "end_date": "1361"},
    "P152": {"end_date": "1386", "start_date": "1306"},
    "P3814": {"end_date": "1136", "start_date": "1042"},
    "P7589": {"start_start_date": "1100", "start_end_date": "1199"},
    "P8LS13536": {"start_start_date": "0700", "start_end_date": "0799"},
    "P6986": {"start_start_date": "0800", "start_end_date": "0899"},
    "P3464": {"start_date": "1011", "end_date": "1075"},
    "P10011": {"start_start_date": "1000", "start_end_date": "1099"},
    "P4301": {"start_date": "1166", "end_date": "1244"},
    "P7840": {"start_start_date": "1000", "start_end_date": "1099"},
    "P00EGS1017975": {"end_date": "1217", "start_date": "1127"},
    "P2890": {"start_date": "1014", "end_date": "1074"},
    "P3097": {"start_start_date": "1100", "start_end_date": "1299"},
    "P3469": {"start_start_date": "1000", "start_end_date": "1099"},
    "P3696": {"start_start_date": "1200", "start_end_date": "1299"},
    "P3832": {"start_start_date": "1100", "start_end_date": "1299"},
    "P5169": {"start_start_date": "1000", "start_end_date": "1099"},
    "P5954": {"start_start_date": "1400", "start_end_date": "1499"},
    "P4862": {"start_start_date": "1100", "start_end_date": "1199"},
    "P3468": {"start_start_date": "1000", "start_end_date": "1099"},
    "P5298": {"start_start_date": "1100", "start_end_date": "1299"},
    "P8408": {"start_start_date": "1200", "start_end_date": "1299"},
}


def get_written_date(start_date, end_date):
    written_date = ""
    if start_date:
        written_date = "ab " + start_date + " "
    if end_date:
        written_date = written_date + "bis " + end_date
    return written_date


def run(*args, **kwargs):
    logger = logging.getLogger(__name__)

    for buda_id, dates in tqdm(LIFESPANS.items()):
        try:
            p = Person.objects.get(external_link__endswith=buda_id)
            if p.start_date:
                logger.warn(
                    "start_date (%s) already present for %s (BUDA ID: %s). Given\n%s",
                    p.start_date,
                    p.id,
                    buda_id,
                    dates,
                )
            else:
                if "start_date" in dates:
                    p.start_date_written = dates["start_date"]
                if "start_start_date" in dates or "start_end_date" in dates:
                    p.start_date_written = get_written_date(
                        dates.get("start_start_date", ""),
                        dates.get("start_end_date", ""),
                    )
            if p.end_date:
                logger.warn(
                    "end_date (%s) already present for %s (BUDA ID: %s). Given\n%s",
                    p.end_date,
                    p.id,
                    buda_id,
                    dates,
                )
            else:
                if "end_date" in dates:
                    p.end_date_written = dates["end_date"]
                if "end_start_date" in dates or "end_end_date" in dates:
                    p.end_date_written = get_written_date(
                        dates.get("end_start_date", ""),
                        dates.get("end_end_date", ""),
                    )

            logger.info("Updated %s with %s", p.id, dates)
            p.save()

        except Person.DoesNotExist:
            logger.warn("Cannot find %s", buda_id)
