from typing import TypedDict, Optional
 
class State(TypedDict):
    query:          str
    category:       str
    sentiment:      str
    response:       str
    resolved:       bool            # True = resolved, False = needs escalation
    web_results:    Optional[str]
    ticket_id:      Optional[str]
    faq_context:    Optional[str]