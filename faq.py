# ── FAQ Data ───────────────────────────────────────────────────────
FAQ_DATA = {
    "🔧 Technical": [
        {
            "q": "Why is my internet connection dropping frequently?",
            "a": "Frequent drops are usually caused by router overheating, outdated firmware, or signal interference. Try restarting your router, moving it to an open space, and checking for firmware updates in the admin panel (usually at 192.168.1.1)."
        },
        {
            "q": "How do I reset my password?",
            "a": "Go to the login page and click 'Forgot Password'. Enter your registered email address and follow the link sent to you. The reset link expires in 30 minutes. If you don't receive the email, check your spam folder."
        },
        {
            "q": "The app crashes when I open it. What should I do?",
            "a": "First, force-close the app and reopen it. If that doesn't help, clear the app cache (Settings → Apps → [App Name] → Clear Cache), then try again. If the issue persists, uninstall and reinstall the latest version."
        },
        {
            "q": "How do I update to the latest software version?",
            "a": "Open the app, go to Settings → About → Check for Updates. On mobile, visit your App Store or Google Play Store and tap Update. We recommend keeping auto-updates enabled to always get the latest fixes and features."
        },
        {
            "q": "I can't log in even with the correct credentials. What's wrong?",
            "a": "This can happen if your account is locked after multiple failed attempts, or if cookies/cache are interfering. Clear your browser cache, try an incognito window, or wait 15 minutes before retrying. Contact support if it continues."
        },
    ],
    "💳 Billing": [
        {
            "q": "I was charged twice this month. How do I get a refund?",
            "a": "Duplicate charges are rare but can happen during payment processing errors. Please contact our billing team at billing@support.com with your transaction IDs. Refunds are processed within 5–7 business days back to your original payment method."
        },
        {
            "q": "How do I cancel my subscription?",
            "a": "Go to Account Settings → Subscription → Cancel Plan. You'll retain access until the end of your current billing period. We do not offer prorated refunds for partial months. You can re-subscribe at any time."
        },
        {
            "q": "Where can I find my invoice or receipt?",
            "a": "All invoices are emailed to your registered address after each billing cycle. You can also download them from Account Settings → Billing History. PDFs are available for the past 24 months."
        },
        {
            "q": "Can I switch from monthly to annual billing?",
            "a": "Yes! Go to Account Settings → Subscription → Change Plan. Switching to annual billing gives you 2 months free. The change takes effect at your next billing date and the difference is prorated."
        },
        {
            "q": "What payment methods do you accept?",
            "a": "We accept all major credit and debit cards (Visa, Mastercard, Amex), PayPal, and bank transfers for annual enterprise plans. Cryptocurrency is not currently supported."
        },
    ],
    "💬 General": [
        {
            "q": "How do I contact customer support?",
            "a": "You can reach us via this chat assistant, by emailing support@company.com, or by calling 1-800-XXX-XXXX (Mon–Fri, 9 AM–6 PM IST). Premium plan users also get access to 24/7 priority support."
        },
        {
            "q": "What are your support hours?",
            "a": "Our AI assistant is available 24/7. Human agents are available Monday to Friday, 9 AM to 6 PM IST. For urgent issues outside these hours, please email us and we'll respond within 4 hours."
        },
        {
            "q": "How do I update my account information?",
            "a": "Log in and navigate to Account Settings → Profile. You can update your name, email, phone number, and profile picture there. Email changes require re-verification via a confirmation link."
        },
        {
            "q": "Is my data safe with you?",
            "a": "Yes. We use AES-256 encryption for data at rest and TLS 1.3 for data in transit. We are SOC 2 Type II and ISO 27001 certified. We never sell your data to third parties. You can request a full data export or deletion at any time."
        },
        {
            "q": "Do you offer a free trial?",
            "a": "Yes! We offer a 14-day free trial with no credit card required. You get full access to all features during the trial. At the end, you can choose a plan or let it expire — your data is retained for 30 days after expiry."
        },
    ],
}

ALL_FAQS = [(cat, item["q"], item["a"]) for cat, items in FAQ_DATA.items() for item in items]

# ── FAQ Search ─────────────────────────────────────────────────────
def search_faqs(search_term: str, category_filter: str) -> str:
    term = search_term.strip().lower()
    results = []

    for cat, q, a in ALL_FAQS:
        if category_filter != "All" and not cat.endswith(category_filter.split()[-1]):
            continue
        if term and term not in q.lower() and term not in a.lower():
            continue
        results.append((cat, q, a))

    if not results:
        return "❌ No FAQs found matching your search. Try a different term or ask the support agent directly."

    html = ""
    for cat, q, a in results:
        html += f"""
        <div class="faq-item">
            <div class="faq-category-tag">{cat}</div>
            <div class="faq-question">Q: {q}</div>
            <div class="faq-answer">{a}</div>
        </div>
        """
    return html
