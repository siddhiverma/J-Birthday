const latestNotices=[
['Kindness','The way you care about people without making a big deal about it.'],
['Patience','You somehow have an impressive amount of it.'],
['Curiosity','You make even a random weekend in Bangalore feel worth exploring.'],
['The way you listen','You actually listen. And remember.'],
['Ambition','Watching how hard you work is genuinely inspiring.'],
['Spontaneity','Coorg was evidence.'],
['Comfort','Somehow, talking to you has always felt easy.'],
['Your very questionable taste in television','Evidence: Traitors, KKK, LockUp, and now GOT'],
['Fun','You have an almost unreasonable ability to make everything more fun.'],
['Hotness','I could write something thoughtful here, but honestly… you’re just really fucking hot. 😌']
];
function renderLatestNotices(){const list=document.getElementById('noticed-list');if(!list)return;list.innerHTML=latestNotices.map(n=>`<article class="notice"><div class="notice-text"><strong>${n[0]}</strong><p>${n[1]}</p></div></article>`).join('');const heading=document.querySelector('#noticed h2');if(heading)heading.textContent='If I had to describe you..';const subtitle=document.querySelector('.noticed-subtitle');if(subtitle)subtitle.textContent='I’d probably run out of words before I ran out of things to say.';const note=document.querySelector('.noticed-note');if(note)note.remove()}
window.renderLatestNotices=renderLatestNotices;renderLatestNotices();
