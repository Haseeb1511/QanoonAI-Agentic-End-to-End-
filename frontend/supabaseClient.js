import { createClient } from "@supabase/supabase-js";

// -------------------- Supabase config --------------------
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;

// -------------------- Create client --------------------
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);




// # It let us do these
// # supabase.auth.signInWithOAuth(), supabase.auth.getSession(), supabase.from("table").select(), etc
// # VITE_API_URL=http://127.0.0.1:8000