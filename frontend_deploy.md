# create file in forned
``vercel.json``
```js

{
    "rewrites": [
        {
            "source": "/(.*)",
            "destination": "/index.html"
        }
    ]
}

```

after deploymned
add the deployed url as env in vercel env
then add that url in supbase also


```
Crucial: You must add your environment variables (like VITE_API_URL, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY) in the Environment Variables section of your Vercel project settings. The .env file is not uploaded to Vercel for security reasons.
Tip: Copy them from your local .env file and paste them into Vercel.
```