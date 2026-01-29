import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Loader2, AlertCircle } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("");

  useEffect(() => {
    console.log("=== Login Component Mounted ===");
    console.log("Current URL:", window.location.href);
    console.log("Search params:", Object.fromEntries(searchParams));

    // Check if already authenticated
    const sessionId = sessionStorage.getItem("user_session");
    if (sessionId) {
      console.log("✅ User already authenticated, navigating to dashboard");
      navigate("/", { replace: true });
      return;
    }

    // Handle Microsoft callback - get all params
    const session = searchParams.get("session");
    const user = searchParams.get("user");
    const userEmail = searchParams.get("email");
    const errorParam = searchParams.get("error");

    console.log("OAuth callback params:", { 
      session: session ? `${session.substring(0, 10)}...` : null, 
      user, 
      userEmail, 
      error: errorParam 
    });

    if (errorParam) {
      console.error("❌ OAuth error:", errorParam);
      
      // Provide user-friendly error messages
      const errorMessages: Record<string, string> = {
        unauthorized_domain: "❌ Access Denied: Only Aspect company accounts (@aspect.co.uk) are allowed. Please use your company Microsoft account.",
        wrong_tenant: "❌ Access Denied: You must be logged into your Aspect company Microsoft account.",
        token_exchange_failed: "❌ Failed to complete Microsoft authentication. Please try again.",
        no_code: "❌ Authentication code missing. Please try again.",
        no_token: "❌ Could not obtain access token. Please try again.",
        user_info_failed: "❌ Could not retrieve user information. Please try again.",
        exception: "❌ An error occurred during authentication. Please try again."
      };
      
      const errorMessage = errorMessages[errorParam] || `❌ Authentication failed: ${errorParam}`;
      setError(errorMessage);
      return;
    }

    // If we have session info from OAuth callback, save and navigate
    if (session && user && userEmail) {
      console.log("✅ OAuth successful, user:", user);
      console.log("📝 Saving session:", session.substring(0, 10) + "...");
      sessionStorage.setItem("user_session", session);
      sessionStorage.setItem("user_data", JSON.stringify({ name: user, email: userEmail }));
      console.log("🔄 Navigating to dashboard...");
      // Use replace to avoid back button issues
      navigate("/", { replace: true });
    }
  }, [navigate, searchParams]);

  const handleMicrosoftLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      window.location.href = "http://localhost:8000/api/auth/microsoft";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start authentication");
      setLoading(false);
    }
  };

  const handleDemoLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email.trim()) {
      setError("Please enter an email");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/auth/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: email, email: email }),
      });

      const data = await response.json();
      sessionStorage.setItem("user_session", data.session_id);
      sessionStorage.setItem("user_data", JSON.stringify({ name: email, email: email }));
      navigate("/");
    } catch (err) {
      setError("Failed to create session. Please try again.");
      console.error("Demo login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-slate-50 flex flex-col items-center justify-center p-4">
      {/* Simplified container */}
      <div className="w-full max-w-md">
        {/* Sign-in card */}
        <div className="bg-white rounded-lg shadow-sm border border-slate-200">
          {/* Header section */}
          <div className="px-8 py-12 border-b border-slate-200">
            <h1 className="text-2xl font-semibold text-slate-900 mb-2">Sign in</h1>
            <p className="text-sm text-slate-600">Fleet Health Monitor</p>
          </div>

          {/* Content section */}
          <div className="px-8 py-8 space-y-6">
            {/* Error Alert */}
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-md flex gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}

            {/* Microsoft Sign-In Button */}
            <button
              onClick={handleMicrosoftLogin}
              disabled={loading}
              className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-medium rounded-md transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <svg className="h-5 w-5 fill-current" viewBox="0 0 24 24">
                    <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6v-11.4H24V24zM11.4 11.4H0V0h11.4v11.4zm12.6 0H12.6V0H24v11.4z" />
                  </svg>
                  <span>Sign in with Microsoft</span>
                </>
              )}
            </button>

            {/* Separator */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-slate-600">or</span>
              </div>
            </div>

            {/* Demo Login Form */}
            <form onSubmit={handleDemoLogin} className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-900 mb-1">
                  Email or phone
                </label>
                <input
                  id="email"
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="someone@example.com"
                  disabled={loading}
                  className="w-full px-4 py-3 border border-slate-300 rounded-md text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-400"
                />
                <p className="mt-1 text-xs text-slate-500">
                  Demo Mode: Type any email to login
                </p>
              </div>

              <button
                type="submit"
                disabled={loading || !email.trim()}
                className="w-full mt-6 py-3 px-4 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-medium rounded-md transition-colors"
              >
                {loading ? "Signing in..." : "Sign in"}
              </button>
            </form>
          </div>

          {/* Footer section */}
          <div className="px-8 py-6 bg-slate-50 border-t border-slate-200 rounded-b-lg">
            <p className="text-xs text-slate-600 text-center">
              Demo Login Available • Password Not Required
            </p>
          </div>
        </div>

        {/* Additional links */}
        <div className="mt-4 text-center text-sm text-slate-600">
          <p>
            Can't access your account?{" "}
            <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
              Get help signing in
            </a>
          </p>
        </div>

        {/* Copyright */}
        <div className="mt-8 text-center text-xs text-slate-500">
          <p>© 2026 Fleet Health Monitor. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}
