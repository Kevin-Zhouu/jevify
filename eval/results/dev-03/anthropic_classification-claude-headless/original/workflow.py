# Setup our environment
import os

import anthropic

MODEL = "claude-haiku-4-5"
client = anthropic.Anthropic(
    # This is the default and can be omitted
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

import textwrap

categories = textwrap.dedent("""<category>
    <label>Billing Inquiries</label>
    <content> Questions about invoices, charges, fees, and premiums Requests for clarification on billing statements Inquiries about payment methods and due dates
    </content>
</category>
<category>
    <label>Policy Administration</label>
    <content> Requests for policy changes, updates, or cancellations Questions about policy renewals and reinstatements Inquiries about adding or removing coverage options
    </content>
</category>
<category>
    <label>Claims Assistance</label>
    <content> Questions about the claims process and filing procedures Requests for help with submitting claim documentation Inquiries about claim status and payout timelines
    </content>
</category>
<category>
    <label>Coverage Explanations</label>
    <content> Questions about what is covered under specific policy types Requests for clarification on coverage limits and exclusions Inquiries about deductibles and out-of-pocket expenses
    </content>
</category>
<category>
    <label>Quotes and Proposals</label>
    <content> Requests for new policy quotes and price comparisons Questions about available discounts and bundling options Inquiries about switching from another insurer
    </content>
</category>
<category>
    <label>Account Management</label>
    <content> Requests for login credentials or password resets Questions about online account features and functionality Inquiries about updating contact or personal information
    </content>
</category>
<category>
    <label>Billing Disputes</label>
    <content> Complaints about unexpected or incorrect charges Requests for refunds or premium adjustments Inquiries about late fees or collection notices
    </content>
</category>
<category>
    <label>Claims Disputes</label>
    <content> Complaints about denied or underpaid claims Requests for reconsideration of claim decisions Inquiries about appealing a claim outcome
    </content>
</category>
<category>
    <label>Policy Comparisons</label>
    <content> Questions about the differences between policy options Requests for help deciding between coverage levels Inquiries about how policies compare to competitors' offerings
    </content>
</category>
<category>
    <label>General Inquiries</label>
    <content> Questions about company contact information or hours of operation Requests for general information about products or services Inquiries that don't fit neatly into other categories
    </content>
</category>""")

def _original_classify(X):
    prompt = (
        textwrap.dedent("""
    You will classify a customer support ticket into one of the following categories:
    <categories>
        {{categories}}
    </categories>

    Here is the customer support ticket:
    <ticket>
        {{ticket}}
    </ticket>

    Respond with just the label of the category between category tags.
    """)
        .replace("{{categories}}", categories)
        .replace("{{ticket}}", X)
    )
    response = client.messages.create(
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "<category>"},
        ],
        stop_sequences=["</category>"],
        max_tokens=4096,
        temperature=0.0,
        model=MODEL,
    )

    # Extract the result from the response
    result = response.content[0].text  # pyright: ignore[reportAttributeAccessIssue]
    return result.strip()


def simple_classify(X):
    import logging
    _logger = logging.getLogger(__name__)

    jev_label = None
    try:
        from jev_decisions import evaluate_category, gate, JEV_MODEL
        label, confidence, raw_body = evaluate_category(X)
        if gate(confidence):
            jev_label = label
            _logger.info("jev path=jev model=%s confidence=%.4f", raw_body.get("model", JEV_MODEL), confidence)
        else:
            _logger.info("jev path=original model=%s jev_model=%s reason=low_confidence confidence=%.4f", MODEL, JEV_MODEL, confidence)
    except Exception as exc:
        reason = str(exc) if str(exc) in ("missing_key", "rate_limit", "model_mismatch", "unknown_label", "invalid_confidence", "invalid_usage", "malformed_response") else "error"
        _logger.info("jev path=original model=%s jev_model=%s reason=%s", MODEL, JEV_MODEL, reason)

    if jev_label is not None:
        return jev_label

    return _original_classify(X)
