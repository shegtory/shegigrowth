$content = @'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ShegiGrowth</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:#f7f6f3;--surface:#ffffff;--surface2:#f0efe9;--border:#e8e6df;
    --text:#1a1916;--text2:#6b6960;--text3:#a8a69e;
    --accent:#2d5be3;--accent-light:#eef1fd;
    --green:#1a7a4a;--green-light:#e8f5ee;
    --amber:#92500a;--amber-light:#fdf3e7;
    --purple:#5b3fa6;--purple-light:#f0ecfb;
    --pink:#a0285a;--pink-light:#fceef5;
    --radius:16px;--radius-sm:10px;
    --nav-bg:rgba(247,246,243,0.92);
  }
  [data-theme="dark"] {
    --bg:#0f0f0d;--surface:#1a1917;--surface2:#242320;--border:#2e2c29;
    --text:#f0ede8;--text2:#9a9790;--text3:#5a5853;
    --accent:#4f7ef5;--accent-light:#1a2340;
    --green:#2db36a;--green-light:#0d2a1a;
    --amber:#d4820f;--amber-light:#2a1e08;
    --purple:#8b6fd4;--purple-light:#1e1730;
    --pink:#d45c8a;--pink-light:#2a0f1a;
    --nav-bg:rgba(15,15,13,0.92);
  }
  *{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
  html,body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;font-size:15px;line-height:1.5;min-height:100vh;transition:background 0.2s,color 0.2s;}
  .nav{position:sticky;top:0;z-index:100;background:var(--nav-bg);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:14px 20px;gap:10px;}
  .nav-logo{font-size:16px;font-weight:500;letter-spacing:-0.3px;flex-shrink:0;}
  .nav-logo span{color:var(--accent);}
  .nav-right{display:flex;align-items:center;gap:8px;}
  .theme-btn{width:32px;height:32px;border-radius:50%;border:1px solid var(--border);background:var(--surface2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;transition:all 0.15s;flex-shrink:0;}
  .theme-btn:active{transform:scale(0.93);}
  .nav-tabs{display:flex;gap:2px;background:var(--surface2);border-radius:10px;padding:3px;}
  .nav-tab{font-size:11px;font-weight:500;padding:6px 10px;border-radius:7px;color:var(--text2);border:none;background:transparent;cursor:pointer;transition:all 0.15s;font-family:'DM Sans',sans-serif;}
  .nav-tab.active{background:var(--surface);color:var(--text);box-shadow:0 1px 3px rgba(0,0,0,0.08);}
  .page{display:none;padding:20px;animation:fadeIn 0.2s ease;}
  .page.active{display:block;}
  @keyframes fadeIn{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:translateY(0);}}
  .stats-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:20px;}
  .stat-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;}
  .stat-val{font-size:28px;font-weight:300;letter-spacing:-1px;font-family:'DM Mono',monospace;color:var(--text);}
  .stat-val.accent{color:var(--accent);}
  .stat-lbl{font-size:11px;color:var(--text3);text-transform:uppercase;letter-spacing:0.6px;margin-top:4px;font-weight:500;}
  .section-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;}
  .section-title{font-size:11px;font-weight:500;color:var(--text3);text-transform:uppercase;letter-spacing:0.8px;}
  .section-badge{font-size:11px;font-weight:500;color:var(--text2);background:var(--surface2);padding:3px 9px;border-radius:20px;}
  .target-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px;display:flex;align-items:center;gap:13px;margin-bottom:8px;transition:all 0.15s;}
  .target-card:active{transform:scale(0.99);}
  .target-card.done{opacity:0.45;}
  .avatar{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:500;flex-shrink:0;font-family:'DM Mono',monospace;}
  .avatar.green{background:var(--green-light);color:var(--green);}
  .avatar.blue{background:var(--accent-light);color:var(--accent);}
  .avatar.purple{background:var(--purple-light);color:var(--purple);}
  .avatar.pink{background:var(--pink-light);color:var(--pink);}
  .avatar.gray{background:var(--surface2);color:var(--text2);}
  .target-info{flex:1;min-width:0;}
  .target-handle{font-size:14px;font-weight:500;letter-spacing:-0.2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .target-meta{font-size:12px;color:var(--text3);margin-top:1px;font-family:'DM Mono',monospace;font-weight:300;}
  .cat-pill{display:inline-flex;align-items:center;gap:4px;font-size:10px;font-weight:500;padding:2px 7px;border-radius:20px;margin-top:5px;letter-spacing:0.2px;}
  .cat-pill.fellow{background:var(--green-light);color:var(--green);}
  .cat-pill.levelup{background:var(--accent-light);color:var(--accent);}
  .cat-pill.gem{background:var(--purple-light);color:var(--purple);}
  .cat-pill.leader{background:var(--pink-light);color:var(--pink);}
  .follow-btn{flex-shrink:0;border:none;cursor:pointer;font-family:'DM Sans',sans-serif;font-weight:500;font-size:13px;padding:8px 16px;border-radius:20px;transition:all 0.15s;}
  .follow-btn.active{background:var(--accent);color:#fff;}
  .follow-btn.active:active{transform:scale(0.97);}
  .follow-btn.done-btn{background:var(--green-light);color:var(--green);}
  .progress-wrap{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:20px;}
  .progress-top{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;}
  .progress-label{font-size:13px;font-weight:500;}
  .progress-count{font-size:13px;font-family:'DM Mono',monospace;font-weight:300;color:var(--text2);}
  .progress-bar-bg{height:5px;background:var(--surface2);border-radius:3px;overflow:hidden;}
  .progress-bar-fill{height:100%;background:var(--accent);border-radius:3px;transition:width 0.4s ease;}
  .chart-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px;margin-bottom:20px;}
  .chart-area{height:100px;display:flex;align-items:flex-end;gap:6px;margin-top:14px;}
  .chart-bar-wrap{flex:1;display:flex;flex-direction:column;align-items:center;gap:5px;}
  .chart-bar{width:100%;border-radius:4px 4px 0 0;background:var(--accent-light);transition:height 0.5s ease;min-height:4px;}
  .chart-bar.highlight{background:var(--accent);}
  .chart-day{font-size:10px;color:var(--text3);font-family:'DM Mono',monospace;}
  .lb-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px;display:flex;align-items:center;gap:13px;margin-bottom:8px;}
  .lb-rank{font-size:13px;font-family:'DM Mono',monospace;font-weight:300;color:var(--text3);width:20px;text-align:center;flex-shrink:0;}
  .lb-rank.top{color:var(--amber);font-weight:500;}
  .lb-info{flex:1;}
  .lb-name{font-size:14px;font-weight:500;}
  .lb-sub{font-size:12px;color:var(--text3);font-family:'DM Mono',monospace;font-weight:300;margin-top:1px;}
  .lb-streak{font-size:13px;font-family:'DM Mono',monospace;font-weight:400;color:var(--text2);}
  .lb-card.me{border-color:var(--accent);background:var(--accent-light);}
  .profile-header{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:22px 20px;margin-bottom:16px;text-align:center;}
  .profile-avatar{width:64px;height:64px;border-radius:50%;background:var(--accent-light);color:var(--accent);font-size:24px;font-weight:500;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-family:'DM Mono',monospace;}
  .profile-name{font-size:18px;font-weight:500;letter-spacing:-0.4px;}
  .profile-handle{font-size:13px;color:var(--text3);font-family:'DM Mono',monospace;font-weight:300;margin-top:3px;}
  .profile-stats{display:flex;gap:0;margin-top:18px;border-top:1px solid var(--border);padding-top:16px;}
  .profile-stat{flex:1;text-align:center;}
  .profile-stat+.profile-stat{border-left:1px solid var(--border);}
  .profile-stat-val{font-size:20px;font-weight:300;font-family:'DM Mono',monospace;letter-spacing:-0.5px;}
  .profile-stat-lbl{font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-top:2px;font-weight:500;}
  .setting-row{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);padding:14px 16px;display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;}
  .setting-lbl{font-size:14px;font-weight:400;}
  .setting-val{font-size:13px;color:var(--text3);font-family:'DM Mono',monospace;font-weight:300;}
  .setting-arrow{font-size:16px;color:var(--text3);}
  .empty-state{text-align:center;padding:50px 20px;}
  .empty-state p{font-size:14px;color:var(--text3);margin-top:8px;}
  .divider{height:1px;background:var(--border);margin:16px 0;}
  .today-banner{background:linear-gradient(135deg,var(--accent) 0%,#1e44c4 100%);border-radius:var(--radius);padding:16px 18px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;}
  .banner-text{color:#fff;}
  .banner-title{font-size:14px;font-weight:500;}
  .banner-sub{font-size:12px;opacity:0.75;margin-top:2px;}
  .banner-icon{font-size:28px;}

  /* SEARCH */
  .search-input-wrap{position:relative;margin-bottom:16px;}
  .search-input{width:100%;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px 16px 12px 42px;font-size:14px;font-family:'DM Sans',sans-serif;color:var(--text);outline:none;transition:border 0.15s;}
  .search-input::placeholder{color:var(--text3);}
  .search-input:focus{border-color:var(--accent);}
  .search-icon{position:absolute;left:14px;top:50%;transform:translateY(-50%);font-size:16px;color:var(--text3);pointer-events:none;}
  .search-btn{width:100%;background:var(--accent);color:#fff;border:none;border-radius:var(--radius-sm);padding:12px;font-size:14px;font-weight:500;font-family:'DM Sans',sans-serif;cursor:pointer;transition:all 0.15s;margin-bottom:20px;}
  .search-btn:active{transform:scale(0.98);}
  .search-btn:disabled{opacity:0.5;cursor:not-allowed;}

  .result-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px;margin-bottom:12px;}
  .result-top{display:flex;align-items:center;gap:13px;margin-bottom:14px;}
  .result-avatar{width:48px;height:48px;border-radius:50%;background:var(--accent-light);color:var(--accent);font-size:18px;font-weight:500;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-family:'DM Mono',monospace;}
  .result-name{font-size:16px;font-weight:500;letter-spacing:-0.3px;}
  .result-handle{font-size:13px;color:var(--text3);font-family:'DM Mono',monospace;font-weight:300;}
  .result-bio{font-size:13px;color:var(--text2);line-height:1.5;margin-bottom:14px;}
  .result-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:14px;}
  .result-stat{background:var(--surface2);border-radius:10px;padding:10px;text-align:center;}
  .result-stat-val{font-size:16px;font-weight:400;font-family:'DM Mono',monospace;letter-spacing:-0.3px;}
  .result-stat-lbl{font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;margin-top:3px;font-weight:500;}
  .result-cat{display:flex;align-items:center;justify-content:space-between;padding-top:12px;border-top:1px solid var(--border);}
  .result-cat-label{font-size:12px;color:var(--text3);font-weight:500;text-transform:uppercase;letter-spacing:0.5px;}
  .search-hint{font-size:13px;color:var(--text3);text-align:center;padding:30px 20px;line-height:1.6;}
  .loading-dots{display:flex;gap:5px;justify-content:center;padding:40px;}
  .loading-dots span{width:7px;height:7px;border-radius:50%;background:var(--accent);animation:dot 1.2s infinite;}
  .loading-dots span:nth-child(2){animation-delay:0.2s;}
  .loading-dots span:nth-child(3){animation-delay:0.4s;}
  @keyframes dot{0%,80%,100%{transform:scale(0.6);opacity:0.3;}40%{transform:scale(1);opacity:1;}}
  .error-msg{background:var(--pink-light);color:var(--pink);border-radius:var(--radius-sm);padding:12px 16px;font-size:13px;margin-bottom:12px;}
</style>
</head>
<body>

<nav class="nav">
  <div class="nav-logo">Shegi<span>Growth</span></div>
  <div class="nav-right">
    <button class="theme-btn" onclick="toggleTheme()" id="theme-btn" title="Toggle theme">☀️</button>
    <div class="nav-tabs">
      <button class="nav-tab active" onclick="showPage('home',this)">Home</button>
      <button class="nav-tab" onclick="showPage('search',this)">Search</button>
      <button class="nav-tab" onclick="showPage('ranks',this)">Ranks</button>
      <button class="nav-tab" onclick="showPage('profile',this)">Me</button>
    </div>
  </div>
</nav>

<!-- HOME -->
<div class="page active" id="page-home">
  <div class="today-banner">
    <div class="banner-text">
      <div class="banner-title">Good morning! Ready to grow?</div>
      <div class="banner-sub">5 targets waiting for you today</div>
    </div>
    <div class="banner-icon">🌱</div>
  </div>
  <div class="stats-row">
    <div class="stat-card">
      <div class="stat-val accent" id="stat-followers">—</div>
      <div class="stat-lbl">Followers</div>
    </div>
    <div class="stat-card">
      <div class="stat-val" id="stat-streak">—</div>
      <div class="stat-lbl">Day Streak 🔥</div>
    </div>
  </div>
  <div class="progress-wrap">
    <div class="progress-top">
      <div class="progress-label">Today's progress</div>
      <div class="progress-count" id="progress-count">0 / 5</div>
    </div>
    <div class="progress-bar-bg">
      <div class="progress-bar-fill" id="progress-bar" style="width:0%"></div>
    </div>
  </div>
  <div class="section-head">
    <div class="section-title">Today's Targets</div>
    <div class="section-badge" id="date-badge">—</div>
  </div>
  <div id="targets-list"><div class="empty-state"><p>Loading targets...</p></div></div>
</div>

<!-- SEARCH -->
<div class="page" id="page-search">
  <div class="section-head" style="margin-bottom:16px;">
    <div class="section-title">Account Lookup</div>
    <div class="section-badge">Twitter Stats</div>
  </div>
  <div class="search-input-wrap">
    <span class="search-icon">@</span>
    <input class="search-input" id="search-input" type="text" placeholder="Enter Twitter handle..." autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" onkeydown="if(event.key==='Enter')doSearch()">
  </div>
  <button class="search-btn" id="search-btn" onclick="doSearch()">Look up account</button>
  <div id="search-result">
    <div class="search-hint">Enter a Twitter handle to see follower count, engagement rate, and growth category.</div>
  </div>
</div>

<!-- RANKS -->
<div class="page" id="page-ranks">
  <div class="section-head" style="margin-bottom:16px;">
    <div class="section-title">Weekly Leaderboard</div>
    <div class="section-badge">Top Streaks</div>
  </div>
  <div id="lb-list">
    <div class="lb-card me">
      <div class="lb-rank top">1</div>
      <div style="width:36px;height:36px;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;font-weight:500;flex-shrink:0;">Y</div>
      <div class="lb-info"><div class="lb-name">You</div><div class="lb-sub">@yourhandle</div></div>
      <div class="lb-streak">7 🔥</div>
    </div>
    <div class="lb-card">
      <div class="lb-rank top">2</div>
      <div style="width:36px;height:36px;border-radius:50%;background:var(--green-light);display:flex;align-items:center;justify-content:center;color:var(--green);font-size:14px;font-weight:500;flex-shrink:0;">A</div>
      <div class="lb-info"><div class="lb-name">Alex</div><div class="lb-sub">@alexbuilds</div></div>
      <div class="lb-streak">6 🔥</div>
    </div>
    <div class="lb-card">
      <div class="lb-rank top">3</div>
      <div style="width:36px;height:36px;border-radius:50%;background:var(--purple-light);display:flex;align-items:center;justify-content:center;color:var(--purple);font-size:14px;font-weight:500;flex-shrink:0;">S</div>
      <div class="lb-info"><div class="lb-name">Sarah</div><div class="lb-sub">@sarahgrows</div></div>
      <div class="lb-streak">5 🔥</div>
    </div>
    <div class="lb-card">
      <div class="lb-rank">4</div>
      <div style="width:36px;height:36px;border-radius:50%;background:var(--surface2);display:flex;align-items:center;justify-content:center;color:var(--text2);font-size:14px;font-weight:500;flex-shrink:0;">M</div>
      <div class="lb-info"><div class="lb-name">Mike</div><div class="lb-sub">@miketweets</div></div>
      <div class="lb-streak">4 🔥</div>
    </div>
    <div class="lb-card">
      <div class="lb-rank">5</div>
      <div style="width:36px;height:36px;border-radius:50%;background:var(--surface2);display:flex;align-items:center;justify-content:center;color:var(--text2);font-size:14px;font-weight:500;flex-shrink:0;">J</div>
      <div class="lb-info"><div class="lb-name">Julia</div><div class="lb-sub">@juliacreates</div></div>
      <div class="lb-streak">3 🔥</div>
    </div>
  </div>
  <div class="divider"></div>
  <div class="chart-card">
    <div class="section-head" style="margin-bottom:0;">
      <div class="section-title">Your growth — 7 days</div>
      <div class="section-badge" id="growth-total">+0</div>
    </div>
    <div class="chart-area">
      <div class="chart-bar-wrap"><div class="chart-bar" style="height:30%"></div><div class="chart-day">M</div></div>
      <div class="chart-bar-wrap"><div class="chart-bar" style="height:45%"></div><div class="chart-day">T</div></div>
      <div class="chart-bar-wrap"><div class="chart-bar" style="height:55%"></div><div class="chart-day">W</div></div>
      <div class="chart-bar-wrap"><div class="chart-bar" style="height:40%"></div><div class="chart-day">T</div></div>
      <div class="chart-bar-wrap"><div class="chart-bar" style="height:70%"></div><div class="chart-day">F</div></div>
      <div class="chart-bar-wrap"><div class="chart-bar" style="height:60%"></div><div class="chart-day">S</div></div>
      <div class="chart-bar-wrap"><div class="chart-bar highlight" style="height:100%"></div><div class="chart-day">S</div></div>
    </div>
  </div>
</div>

<!-- PROFILE -->
<div class="page" id="page-profile">
  <div class="profile-header">
    <div class="profile-avatar" id="profile-avatar">?</div>
    <div class="profile-name" id="profile-name">Your Name</div>
    <div class="profile-handle" id="profile-handle">@handle</div>
    <div class="profile-stats">
      <div class="profile-stat"><div class="profile-stat-val" id="p-followers">—</div><div class="profile-stat-lbl">Followers</div></div>
      <div class="profile-stat"><div class="profile-stat-val" id="p-streak">—</div><div class="profile-stat-lbl">Streak</div></div>
      <div class="profile-stat"><div class="profile-stat-val" id="p-done">—</div><div class="profile-stat-lbl">Followed</div></div>
    </div>
  </div>
  <div class="section-head"><div class="section-title">Settings</div></div>
  <div class="setting-row">
    <div class="setting-lbl">Twitter Account</div>
    <div style="display:flex;align-items:center;gap:8px;"><div class="setting-val" id="setting-handle">Not connected</div><div class="setting-arrow">›</div></div>
  </div>
  <div class="setting-row">
    <div class="setting-lbl">Daily Reminder</div>
    <div style="display:flex;align-items:center;gap:8px;"><div class="setting-val">09:00 AM</div><div class="setting-arrow">›</div></div>
  </div>
  <div class="setting-row">
    <div class="setting-lbl">Niche</div>
    <div style="display:flex;align-items:center;gap:8px;"><div class="setting-val" id="setting-niche">Not set</div><div class="setting-arrow">›</div></div>
  </div>
  <div class="setting-row" onclick="toggleTheme()" style="cursor:pointer;">
    <div class="setting-lbl">Dark Mode</div>
    <div style="display:flex;align-items:center;gap:8px;"><div class="setting-val" id="theme-label">Off</div><div class="setting-arrow">›</div></div>
  </div>
  <div class="divider"></div>
  <div class="section-head"><div class="section-title">About</div></div>
  <div class="setting-row"><div class="setting-lbl">Version</div><div class="setting-val">1.0.0</div></div>
</div>

<script>
const tg = window.Telegram?.WebApp;
if(tg){tg.expand();}
const telegram_id = tg?.initDataUnsafe?.user?.id;
const tg_user = tg?.initDataUnsafe?.user;

// THEME
let isDark = localStorage.getItem('theme')==='dark';
function applyTheme(){
  document.documentElement.setAttribute('data-theme', isDark?'dark':'light');
  document.getElementById('theme-btn').textContent = isDark?'🌙':'☀️';
  document.getElementById('theme-label').textContent = isDark?'On':'Off';
  if(tg){tg.setHeaderColor(isDark?'#0f0f0d':'#f7f6f3');}
}
function toggleTheme(){
  isDark=!isDark;
  localStorage.setItem('theme',isDark?'dark':'light');
  applyTheme();
}
applyTheme();

const catMap={
  'Fellow Traveler':{label:'🌱 Fellow Traveler',cls:'fellow',avatarCls:'green'},
  'One Level Up':{label:'🎯 One Level Up',cls:'levelup',avatarCls:'blue'},
  'Hidden Gem':{label:'💎 Hidden Gem',cls:'gem',avatarCls:'purple'},
  'Niche Leader':{label:'👑 Niche Leader',cls:'leader',avatarCls:'pink'}
};

function getCategory(followers, engRate){
  if(followers>50000) return 'Niche Leader';
  if(engRate>5 && followers<3000) return 'Hidden Gem';
  if(followers>5000) return 'One Level Up';
  return 'Fellow Traveler';
}

function fmtNum(n){
  if(n>=1000000) return (n/1000000).toFixed(1)+'M';
  if(n>=1000) return (n/1000).toFixed(1)+'k';
  return n.toString();
}

function showPage(name,el){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('page-'+name).classList.add('active');
  if(el) el.classList.add('active');
}

function setDate(){
  const d=new Date();
  document.getElementById('date-badge').textContent=d.toLocaleDateString('en-US',{month:'short',day:'numeric'});
}

async function loadStats(){
  if(!telegram_id){renderMockStats();return;}
  try{
    const res=await fetch('/api/stats?telegram_id='+telegram_id);
    const data=await res.json();
    const f=data.follower_count??0;
    const s=data.streak??0;
    document.getElementById('stat-followers').textContent=fmtNum(f);
    document.getElementById('stat-streak').textContent=s;
    document.getElementById('p-followers').textContent=fmtNum(f);
    document.getElementById('p-streak').textContent=s;
    document.getElementById('p-done').textContent=data.total_done??'—';
    if(data.twitter_handle){
      document.getElementById('profile-handle').textContent='@'+data.twitter_handle;
      document.getElementById('setting-handle').textContent='@'+data.twitter_handle;
      document.getElementById('profile-avatar').textContent=data.twitter_handle[0].toUpperCase();
    }
    if(data.niche) document.getElementById('setting-niche').textContent=data.niche;
  }catch(e){renderMockStats();}
}

function renderMockStats(){
  document.getElementById('stat-followers').textContent='1.2k';
  document.getElementById('stat-streak').textContent='7';
  document.getElementById('p-followers').textContent='1.2k';
  document.getElementById('p-streak').textContent='7';
  document.getElementById('p-done').textContent='34';
}

if(tg_user){
  const name=[tg_user.first_name,tg_user.last_name].filter(Boolean).join(' ');
  document.getElementById('profile-name').textContent=name||'Your Name';
  document.getElementById('profile-avatar').textContent=(tg_user.first_name||'U')[0].toUpperCase();
}

let doneCount=0;
function updateProgress(done,total){
  doneCount=done;
  document.getElementById('progress-count').textContent=done+' / '+total;
  document.getElementById('progress-bar').style.width=((done/total)*100)+'%';
}

async function loadTargets(){
  const list=document.getElementById('targets-list');
  if(!telegram_id){list.innerHTML=renderMockTargets();return;}
  try{
    const res=await fetch('/api/targets?telegram_id='+telegram_id);
    const data=await res.json();
    if(!data.targets||data.targets.length===0){
      list.innerHTML='<div class="empty-state"><p>No targets yet — come back tomorrow! 🌅</p></div>';
      return;
    }
    const done=data.targets.filter(t=>t.is_done).length;
    updateProgress(done,data.targets.length);
    list.innerHTML=data.targets.map(t=>renderCard(t)).join('');
  }catch(e){list.innerHTML=renderMockTargets();}
}

function renderCard(t){
  const target=t.targets||t;
  const cat=catMap[target.category]||{label:target.category,cls:'fellow',avatarCls:'green'};
  const done=t.is_done;
  const initial=(target.twitter_handle||'?')[0].toUpperCase();
  return '<div class="target-card '+(done?'done':'')+'" id="card-'+t.id+'">'
    +'<div class="avatar '+cat.avatarCls+'">'+initial+'</div>'
    +'<div class="target-info">'
    +'<div class="target-handle">@'+(target.twitter_handle||'unknown')+'</div>'
    +'<div class="target-meta">'+((target.follower_count||0).toLocaleString())+' followers</div>'
    +'<span class="cat-pill '+cat.cls+'">'+cat.label+'</span>'
    +'</div>'
    +'<button class="follow-btn '+(done?'done-btn':'active')+'" '
    +(done?'disabled':'onclick="followTarget(\''+t.id+'\',\''+target.twitter_handle+'\')"')+'>'
    +(done?'✓ Done':'Follow')+'</button></div>';
}

function renderMockTargets(){
  const mocks=[
    {id:'m1',is_done:true, targets:{twitter_handle:'alexgrowth',   follower_count:2100, category:'Fellow Traveler'}},
    {id:'m2',is_done:false,targets:{twitter_handle:'marketingmike',follower_count:5400, category:'One Level Up'}},
    {id:'m3',is_done:false,targets:{twitter_handle:'sarahbuilds',  follower_count:980,  category:'Hidden Gem'}},
    {id:'m4',is_done:false,targets:{twitter_handle:'nicheleader',  follower_count:48200,category:'Niche Leader'}},
    {id:'m5',is_done:false,targets:{twitter_handle:'techstartup_t',follower_count:1850, category:'Fellow Traveler'}}
  ];
  updateProgress(mocks.filter(m=>m.is_done).length,mocks.length);
  return mocks.map(t=>renderCard(t)).join('');
}

async function followTarget(daily_id,handle){
  window.open('https://twitter.com/'+handle,'_blank');
  const card=document.getElementById('card-'+daily_id);
  card.classList.add('done');
  const btn=card.querySelector('.follow-btn');
  btn.textContent='✓ Done';btn.className='follow-btn done-btn';btn.disabled=true;btn.onclick=null;
  if(!telegram_id){updateProgress(doneCount+1,5);return;}
  try{
    await fetch('/api/done',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id,target_id:daily_id})});
    loadStats();
    updateProgress(document.querySelectorAll('.target-card.done').length,5);
  }catch(e){}
}

// SEARCH
async function doSearch(){
  const inp=document.getElementById('search-input');
  const handle=inp.value.replace('@','').trim();
  if(!handle) return;
  const btn=document.getElementById('search-btn');
  const result=document.getElementById('search-result');
  btn.disabled=true;
  btn.textContent='Looking up...';
  result.innerHTML='<div class="loading-dots"><span></span><span></span><span></span></div>';
  try{
    const res=await fetch('/api/lookup?handle='+encodeURIComponent(handle));
    if(!res.ok) throw new Error('not found');
    const data=await res.json();
    const followers=data.followers_count||0;
    const following=data.following_count||0;
    const tweets=data.tweet_count||0;
    const engRate=data.engagement_rate||((Math.random()*4+1).toFixed(1));
    const catKey=getCategory(followers,parseFloat(engRate));
    const cat=catMap[catKey];
    const initial=(data.name||handle)[0].toUpperCase();
    result.innerHTML='<div class="result-card">'
      +'<div class="result-top">'
      +'<div class="result-avatar">'+initial+'</div>'
      +'<div><div class="result-name">'+(data.name||handle)+'</div>'
      +'<div class="result-handle">@'+handle+'</div></div>'
      +'</div>'
      +(data.description?'<div class="result-bio">'+data.description+'</div>':'')
      +'<div class="result-stats">'
      +'<div class="result-stat"><div class="result-stat-val">'+fmtNum(followers)+'</div><div class="result-stat-lbl">Followers</div></div>'
      +'<div class="result-stat"><div class="result-stat-val">'+fmtNum(following)+'</div><div class="result-stat-lbl">Following</div></div>'
      +'<div class="result-stat"><div class="result-stat-val">'+engRate+'%</div><div class="result-stat-lbl">Eng. Rate</div></div>'
      +'</div>'
      +'<div class="result-cat">'
      +'<div class="result-cat-label">Category</div>'
      +'<span class="cat-pill '+cat.cls+'">'+cat.label+'</span>'
      +'</div></div>';
  }catch(e){
    result.innerHTML='<div class="error-msg">Account not found or API error. Make sure the handle is correct.</div>'
      +'<div class="search-hint">This feature requires the Twitter API to be connected.</div>';
  }
  btn.disabled=false;
  btn.textContent='Look up account';
}

setDate();
loadStats();
loadTargets();
</script>
</body>
</html>
'@
Set-Content -Path "static\index.html" -Value $content -Encoding UTF8
Write-Host "Done! static\index.html updated."
