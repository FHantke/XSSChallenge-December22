# Solution
__SPOILER__

In this section, I describe the steps needed to solve the challenge. All steps are implemented in `malicious_app.py` (variant 1 is medium, variant 2 is hard). The parts that are needed to solve the hard version are marked accordingly.

__Steps to solve the challenge:__
1. Create a blog site with content that steals the CSRF token of your victim. You can achieve this either via the `base` tag or a submit button with the `form` attribute (see function `prepare`). Both variants send the token to your server.
2. When you receive the token, create a blog site that contains a CSRF with your final XSS payload (next steps). Redirect the victim connected to your server to your second blog site.
3. XSS Sink: Due to the CSP, it is challenging to execute malicious JS. Luckily, the CSP is `strict-dynamic`, which means script tags created in the context of a valid script tag are executed even without a valid nonce. Only one line of code meets these preconditions, and it's inside the JS function `update_tags`.
4. XSS Payload 
	- `medium`: For the medium payload, you can inject XSS payload into the tags of the victim. Since the code only copies the tag into the `querySelector` inside the `innerText` of a script tag, the payload can escape this function with quotes and append our own `alert` payload (`create_csrf` 1)
	- `hard`: Due to the filter removing non-alphanumeric characters from tags, the payload from the previous version does not work. Instead, the payload can bypass the server-side HTML sanitizer to break out of the textarea. In the example payload (`create_csrf` 2), we use an mXSS trick that was also used to XSS the Google search ([more details](https://www.acunetix.com/blog/web-security-zone/mutation-xss-in-google-search/)). To break out of the textarea, the payload must add a closing textarea tag. To avoid the element from closing the textarea in the CSRF payload, the `<` and `>` must be encoded. Finally, you can use a dangling markup trick ([more details](https://lcamtuf.coredump.cx/postxss/)) to make the tag input invalid. As a result, the line `form_element.children[form_element.childElementCount - 2];` will select our input. The beginning of the `xss_payload` works similarly to the `medium` payload.
