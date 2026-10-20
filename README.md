# Ninety Sure

A daily game about knowing how sure you really are. Each day has 10 questions. For each one, the player drags two calipers around the range they're 90% sure contains the answer.

This folder is the whole website. It has no server, no database and no build step, so any free static host can run it.

## What's in the folder

| File | What it is |
|---|---|
| `index.html` | The game itself |
| `questions.js` | All 1,990 questions, in the order the days use them |
| `favicon.svg`, `icon-512.png` | Browser tab icon and phone home-screen icon |
| `og-image.png` | The preview picture shown when someone shares the link |
| `CREDITS.md` | Where the data comes from, and its licences |
| `source/` | The script that made `questions.js` (only needed if you want to rebuild it) |

## Put it online

### Option 1: Netlify Drop (easiest, about 2 minutes)

1. Unzip `ninety-sure.zip`.
2. Go to **app.netlify.com/drop**.
3. Drag the `ninety-sure` folder onto the page.
4. Netlify gives you a link like `random-name-123.netlify.app`. The game is live.
5. Make a free Netlify account when it asks, or the site is deleted after an hour. In the site settings you can rename it, for example to `ninetysure.netlify.app`.

### Option 2: GitHub Pages

1. On github.com, create a new **public** repository, for example `ninety-sure`.
2. Click **Add file → Upload files** and drag in everything **inside** the `ninety-sure` folder. `index.html` must be at the top level, not inside a subfolder. Click **Commit changes**.
3. Go to **Settings → Pages**. Under "Build and deployment", choose **Deploy from a branch**, then branch **main** and folder **/ (root)**. Click **Save**.
4. After a minute or two the game is live at `https://YOUR-USERNAME.github.io/ninety-sure/`.

### One thing to do after it's online

Social sites need the full address of the preview picture. Open `index.html`, find this line:

```html
<meta property="og:image" content="og-image.png">
```

and change it to your real address, for example:

```html
<meta property="og:image" content="https://YOUR-USERNAME.github.io/ninety-sure/og-image.png">
```

Upload the changed file again.

## How the daily schedule works

- Day 1 is **5 October 2026** (`LAUNCH_DAY` in `index.html`). Day 1 gets questions 1–10, day 2 gets 11–20, and so on.
- 1,990 questions give **199 days without a single repeat**, up to **21 April 2027**. After that the cycle starts again from question 1.
- Everyone in the world gets the same 10 questions on the same date (by their own clock).
- **Past games** in the menu let players play any earlier day. Their first score for each day is kept.
- **Practice rounds** only use questions from days that have already happened, so practice never spoils a future day.

To add more days, add new questions to the **end** of `questions.js`. Never reorder the existing ones, or past days will change. Each question is one line in this shape:

```js
["unique_id", "Question text?", answer, "unit", "log", lowest, highest, "Note shown after answering.", "facts"]
```

- `log` suits amounts that can span many sizes (heights, distances, counts).
- `year` is for calendar years. Use negative numbers for BC.
- `lin` is for percentages and temperatures.
- `lowest` and `highest` are the ends of the slider. Keep the answer well inside them, not near an edge.

## Saved data and accounts

Scores, streaks, themes and stats are saved in each player's own browser. The "accounts" popup says that synced history and the leaderboard are coming soon. Those need a server, such as Supabase, which can be added later.

## Checking it on your own computer

You can double-click `index.html` to play it. To test it exactly as it will run online, start a tiny local server in the folder:

```
python3 -m http.server 8000
```

Then open http://localhost:8000.
