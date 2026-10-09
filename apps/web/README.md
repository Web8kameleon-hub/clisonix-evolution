# Next.js project

[Next.js](https://nextjs.org)project

 bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Required Billing Environment Variables

Set these variables before using the pricing page:

```bash
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_replace_with_new_key
NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID=prctbl_replace_with_new_id
```

Notes:

- Never hardcode Stripe keys in source files.
- Rotate keys in Stripe Dashboard and update deployment secrets immediately.
- If key rotation causes temporary mismatch, update both variables together.

## AdSense Setup (Next.js)

Set these variables to enable Google AdSense:

```bash
NEXT_PUBLIC_GOOGLE_ADSENSE_ID=ca-pub-XXXXXXXXXXXXXXXX
ADSENSE_SLOT_FOOTER=1234567890
ADSENSE_SLOT_SIDEBAR=1234567890
ADSENSE_SLOT_ARTICLE_TOP=1234567890
ADSENSE_SLOT_ARTICLE_BOTTOM=1234567890
```

Alternative source (server/runtime):

```bash
GOOGLE_ADSENSE_PUBLISHER_ID=ca-pub-XXXXXXXXXXXXXXXX
```

Optional review flag (crawler visibility):

```bash
ADSENSE_REVIEW_MODE=true
```

Notes:

- `NEXT_PUBLIC_GOOGLE_ADSENSE_ID` is preferred for client/runtime visibility.
- `GOOGLE_ADSENSE_PUBLISHER_ID` is also supported as runtime fallback.
- `ADSENSE_REVIEW_MODE=true` injects the AdSense script into initial HTML (for review/preparation visibility) while keeping default behavior unchanged when unset.
- In production, explicit AdSense env config is required by default.
- `ads.txt` is served dynamically at `/ads.txt` from `app/ads.txt/route.ts`.
- The `AdSenseSlot` component reserves layout space by default (`minHeight=250`) to reduce CLS.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
