// Chinese lunisolar calendar — Hồ Ngọc Đức's astronomical algorithm
// (new moons + solar terms), computed for China time, UTC+8.

const LUNAR_TZ = 8;

const STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
const BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const ANIMALS = ['Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake', 'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Pig'];
const MONTHS = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊'];
const DIGITS = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];

function _int(d) { return Math.floor(d); }

function jdFromDate(dd, mm, yy) {
    let a = _int((14 - mm) / 12);
    let y = yy + 4800 - a;
    let m = mm + 12 * a - 3;
    let jd = dd + _int((153 * m + 2) / 5) + 365 * y + _int(y / 4) - _int(y / 100) + _int(y / 400) - 32045;
    if (jd < 2299161)
        jd = dd + _int((153 * m + 2) / 5) + 365 * y + _int(y / 4) - 32083;
    return jd;
}

function _newMoon(k) {
    let T = k / 1236.85, T2 = T * T, T3 = T2 * T, dr = Math.PI / 180;
    let Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3;
    Jd1 += 0.00033 * Math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr);
    let M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3;
    let Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3;
    let F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3;
    let C1 = (0.1734 - 0.000393 * T) * Math.sin(M * dr) + 0.0021 * Math.sin(2 * dr * M);
    C1 = C1 - 0.4068 * Math.sin(Mpr * dr) + 0.0161 * Math.sin(dr * 2 * Mpr);
    C1 = C1 - 0.0004 * Math.sin(dr * 3 * Mpr);
    C1 = C1 + 0.0104 * Math.sin(dr * 2 * F) - 0.0051 * Math.sin(dr * (M + Mpr));
    C1 = C1 - 0.0074 * Math.sin(dr * (M - Mpr)) + 0.0004 * Math.sin(dr * (2 * F + M));
    C1 = C1 - 0.0004 * Math.sin(dr * (2 * F - M)) - 0.0006 * Math.sin(dr * (2 * F + Mpr));
    C1 = C1 + 0.0010 * Math.sin(dr * (2 * F - Mpr)) + 0.0005 * Math.sin(dr * (2 * Mpr + M));
    let deltat = T < -11
        ? 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
        : -0.000278 + 0.000265 * T + 0.000262 * T2;
    return Jd1 + C1 - deltat;
}

function _newMoonDay(k, tz) { return _int(_newMoon(k) + 0.5 + tz / 24); }

function _sunLongitude(jdn) { // 0..11, which 30° sector the sun is in
    let T = (jdn - 2451545.0) / 36525, T2 = T * T, dr = Math.PI / 180;
    let M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2;
    let L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2;
    let DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * Math.sin(dr * M);
    DL += (0.019993 - 0.000101 * T) * Math.sin(dr * 2 * M) + 0.000290 * Math.sin(dr * 3 * M);
    let L = (L0 + DL) * dr;
    L = L - Math.PI * 2 * _int(L / (Math.PI * 2));
    return _int(L / Math.PI * 6);
}

function _sunLongitudeAt(dayNumber, tz) { return _sunLongitude(dayNumber - 0.5 - tz / 24); }

function _lunarMonth11(yy, tz) {
    let off = jdFromDate(31, 12, yy) - 2415021;
    let k = _int(off / 29.530588853);
    let nm = _newMoonDay(k, tz);
    if (_sunLongitudeAt(nm, tz) >= 9)
        nm = _newMoonDay(k - 1, tz);
    return nm;
}

function _leapMonthOffset(a11, tz) {
    let k = _int((a11 - 2415021.076998695) / 29.530588853 + 0.5);
    let last, i = 1;
    let arc = _sunLongitudeAt(_newMoonDay(k + i, tz), tz);
    do {
        last = arc;
        i++;
        arc = _sunLongitudeAt(_newMoonDay(k + i, tz), tz);
    } while (arc != last && i < 14);
    return i - 1;
}

// returns { day, month, year, leap, jd }
function solarToLunar(dd, mm, yy, tz = LUNAR_TZ) {
    let dayNumber = jdFromDate(dd, mm, yy);
    let k = _int((dayNumber - 2415021.076998695) / 29.530588853);
    let monthStart = _newMoonDay(k + 1, tz);
    if (monthStart > dayNumber)
        monthStart = _newMoonDay(k, tz);
    let a11 = _lunarMonth11(yy, tz), b11 = a11, lunarYear;
    if (a11 >= monthStart) {
        lunarYear = yy;
        a11 = _lunarMonth11(yy - 1, tz);
    } else {
        lunarYear = yy + 1;
        b11 = _lunarMonth11(yy + 1, tz);
    }
    let lunarDay = dayNumber - monthStart + 1;
    let diff = _int((monthStart - a11) / 29);
    let leap = false;
    let lunarMonth = diff + 11;
    if (b11 - a11 > 365) {
        let leapMonthDiff = _leapMonthOffset(a11, tz);
        if (diff >= leapMonthDiff) {
            lunarMonth = diff + 10;
            if (diff == leapMonthDiff)
                leap = true;
        }
    }
    if (lunarMonth > 12)
        lunarMonth -= 12;
    if (lunarMonth >= 11 && diff < 4)
        lunarYear -= 1;
    return { day: lunarDay, month: lunarMonth, year: lunarYear, leap: leap, jd: dayNumber };
}

function lunarForDate(date) {
    return solarToLunar(date.getDate(), date.getMonth() + 1, date.getFullYear());
}

// 初一 … 初十, 十一 … 十九, 二十, 廿一 … 廿九, 三十
function chineseDay(d) {
    if (d <= 10) return '初' + DIGITS[d];
    if (d < 20) return '十' + DIGITS[d - 10];
    if (d == 20) return '二十';
    if (d < 30) return '廿' + DIGITS[d - 20];
    return '三十';
}

function chineseMonth(l) { return (l.leap ? '闰' : '') + MONTHS[l.month - 1] + '月'; }

function yearStemBranch(y) { return STEMS[(y + 6) % 10] + BRANCHES[(y + 8) % 12]; }

function dayStemBranch(jd) { return STEMS[(jd + 9) % 10] + BRANCHES[(jd + 1) % 12]; }

function yearAnimal(y) { return ANIMALS[(y + 8) % 12]; }

// text inside a day cell: day/month on the 1st of a lunar month, else just the day
function cellText(l) { return l.day == 1 ? `1/${l.month}${l.leap ? '*' : ''}` : String(l.day); }

// summary line under the grid
function summary(date) {
    let l = lunarForDate(date);
    return `Lunar ${l.day}/${l.month}/${l.year}${l.leap ? ' (leap month)' : ''}  ·  year of the ${yearAnimal(l.year)}`;
}
