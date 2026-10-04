import { API_URL } from "./stream.js";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, options);
  } catch {
    throw new ApiError("Cannot reach the support service. Is the backend running?", 0);
  }

  if (!response.ok) {
    let message = `The support service returned an error (${response.status}).`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // keep the generic message
    }
    throw new ApiError(message, response.status);
  }

  return response.json();
}

export const listTickets = () => request("/team/tickets?limit=100");

export const getConversation = (id, customerId) =>
  request(`/conversations/${encodeURIComponent(id)}?customer_id=${encodeURIComponent(customerId)}`);

export const getTeamConversation = (id) => request(`/team/conversations/${encodeURIComponent(id)}`);

export const getTicket = (id) => request(`/team/tickets/${encodeURIComponent(id)}`);

export const resolveTicket = (id, humanReply) =>
  request(`/team/tickets/${encodeURIComponent(id)}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ human_reply: humanReply }),
  });
