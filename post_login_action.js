/**
 * Auth0 Action - trigger: Login / Post Login
 * Adds a custom claim "agent_id" to the ID token AND the access token,
 * so it shows up when you decode either token at jwt.io.
 * Custom claims need a namespace (a URL you own or make up), so the claim name
 * ends up as  https://securenova.example/agent_id
 */
exports.onExecutePostLogin = async (event, api) => {
  const namespace = "https://securenova.local/";
  const agentId = "securenova-support-agent-01";   // identifies which AI agent acts for this user

  api.idToken.setCustomClaim(namespace + "agent_id", agentId);
  api.accessToken.setCustomClaim(namespace + "agent_id", agentId);
};
