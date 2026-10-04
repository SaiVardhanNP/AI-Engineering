// The demo has no login, so the visitor picks which fake customer they are.
// These match the rows seeded by backend/scripts/seed_db.py.
export const CUSTOMERS = [
  {
    id: "cus_001",
    name: "Alice Rao",
    scenario: "Charged twice, subscription inactive, auth errors",
    starter:
      "I was charged twice for my Pro subscription. My subscription still shows inactive, and my dashboard is returning an authentication error.",
  },
  {
    id: "cus_002",
    name: "Bob Mehta",
    scenario: "Healthy account, nothing is wrong",
    starter: "I think I was charged twice this month. Can you check my payments?",
  },
  {
    id: "cus_003",
    name: "Carol Singh",
    scenario: "Card declined, project paused",
    starter: "My project got paused and my dashboard says there is an unpaid invoice. I don't understand why.",
  },
  {
    id: "cus_004",
    name: "Dan Iyer",
    scenario: "Invoice higher than the plan price",
    starter: "Why was my last invoice $61.40 when the Pro plan is $25?",
  },
  {
    id: "cus_005",
    name: "Eve Kapoor",
    scenario: "Login redirect errors in her app",
    starter: "Users of my app get an error when they log in and the redirect after login fails.",
  },
  {
    id: "cus_006",
    name: "Frank Nair",
    scenario: "Duplicate charge already refunded",
    starter: "I was charged twice for my Pro subscription last month and I want a refund.",
  },
];
