# The Ops Table — website aur automation

Is repo mein ye 3 cheezein hain:

| Kya | File | Kaam |
|---|---|---|
| Website | `index.html`, `assets/style.css`, `config.js` | Landing page, chapters, FAQ, "Apply to join" |
| Ops Radar | `radar.html` + `scripts/collect_news.py` + `.github/workflows/collect-news.yml` | Roz subah 5 regions ki logistics headlines apne aap update hoti hain |
| Application screener | `members/screen_applications.py` | Google Form ke applications ko score karke shortlist banata hai |

Python script sirf Python ki standard library use karti hai, isliye **kuch install nahi karna**.

---

## Stealth rules (pehle ye padho)

- GitHub account **brand Gmail** se banao (jaise theopstable@gmail.com), personal email se nahi.
- Profile mein apna naam, photo ya company mat daalo. Username brand jaisa rakho, jaise `theopstable`.
- `members/*.csv` files kabhi upload mat karna, kyunki unme logon ka data hota hai. `.gitignore` inhe already rokta hai.

---

## Step 1: GitHub account (10 min)

1. https://github.com/signup pe jao aur brand Gmail se account banao.
2. Settings → Password and authentication → **Two-factor authentication** on karo.

## Step 2: Repository banao (5 min)

1. Upar right mein **+** → **New repository** pe click karo.
2. Name `opstable` rakho aur **Public** chuno. Free account pe website (GitHub Pages) sirf public repo pe chalti hai. Isme koi personal info nahi hai, toh public rakhna safe hai.
3. **Create repository** dabao.

## Step 3: Files upload karo (10 min)

1. Repo page pe **"uploading an existing file"** link pe click karo.
2. Zip kholo aur andar ki saari files aur folders (`index.html`, `radar.html`, `config.js`, `feeds.json`, `assets`, `data`, `scripts`, `members`, `README.md`, `.gitignore`) browser mein drag karo.
3. Neeche **Commit changes** dabao.

**`.github` folder alag se daalna padega**, kyunki ye hidden folder hai aur drag mein aksar chhoot jaata hai:
1. **Add file** → **Create new file** pe jao.
2. Naam ki jagah exactly ye likho: `.github/workflows/collect-news.yml`
3. Zip ki `.github/workflows/collect-news.yml` file kholo, uska poora text copy karo aur yahan paste karo.
4. **Commit changes** dabao.

## Step 4: Website live karo (5 min)

1. Repo mein **Settings** → **Pages** pe jao.
2. Source: **Deploy from a branch** → Branch: **main**, folder **/ (root)** → **Save**.
3. 1–2 minute mein website live ho jayegi: `https://<username>.github.io/opstable/`

## Step 5: Ops Radar automation on karo (5 min)

1. **Settings** → **Actions** → **General** pe jao. Neeche **Workflow permissions** mein **Read and write permissions** chuno aur **Save** karo.
2. Upar **Actions** tab pe jao. "Collect Ops Radar news" pe click karo, phir **Run workflow** → **Run workflow** dabao.
3. 1 minute baad green ✓ aayega. Uske baad `radar.html` pe headlines dikhengi.
4. Iske baad ye **roz subah 5:47 IST** pe khud chalega.

Red ✗ aaye toh us run pe click karo, log ka screenshot lo aur Claude ko bhejo.

## Step 6: Apne links daalo (5 min)

1. Brand Gmail se ek **Google Form** banao (forms.google.com) aur usme ye sawaal daalo, kyunki screener inhi naamon ko padhta hai:
   - Full name
   - Current role / designation
   - Company
   - Industry
   - Total years of experience
   - City / Country
   - LinkedIn profile
   - Why do you want to join?
2. Form ka **Send** → link copy karo.
3. GitHub mein `config.js` kholo → ✏️ (edit) pe click karo → `APPLY_FORM_URL` mein apna link daalo, aur `NEWSLETTER_URL` mein LinkedIn page ka link → **Commit changes**.
4. Naam final ho jaaye toh `BRAND_NAME` bhi isi file mein badal dena. Poori website mein naam apne aap badal jayega.

---

## Applications screen karna (har hafte, 2 min)

1. Google Form → **Responses** → hare Sheets icon pe click karo → **File → Download → CSV**.
2. File ka naam `applications.csv` rakho aur apne computer pe is repo ke `members` folder mein daalo.
3. Terminal ya Command Prompt us folder mein kholo aur chalao:
   ```
   python members/screen_applications.py
   ```
4. `members/shortlist.csv` ban jayegi, jisme har applicant ka **Score** aur **Suggestion** (Approve / Review / Hold) hoga.
5. Final faisla aapka hai. Review wale logon ko Command Room mein **Member Screener** agent ko de sakte ho.

## Ops Radar ke regions ya keywords badalna

`feeds.json` edit karo. `regions` mein naya region ya feed link jodo, aur `keywords` mein naye shabd. Agle run se badlav dikhega.

## Baad mein (jab members 100+ ho jaayein)

- **Apna domain:** `.com` khareedo, aur Settings → Pages → Custom domain mein daalo.
- **Newsletter:** Beehiiv ya Substack, brand Gmail se.
