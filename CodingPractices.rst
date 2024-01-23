============================
Recommended Coding Practices
============================

This document recommends certain practices for developing code documentation
so that ECLdoc can rendered it as a professional looking document, and so that
the resulting documentation is largely consistent from project to project.

Use of HTML tags:

ECLdoc ignores the line formatting of documentation strings and treats end-of-line
as a space.  Comments that are formatted as multiple lines with bullet-lists or
other structure will be rendered as a run-on paragraph, and may be difficult to
follow without adding additional markup to improve readability.

For example, the following comment section:

/**
  * This is the warp drive implementation module
  * It serves three purposes:
  * - The first purpose
  * - The second purpose
  * - The third purpose
  **/

This would be rendered by ECLdoc as:

This is the warp drive implementation module It serves three purposes: - The
first purpose - The second purpose - The third purpose

ECLdoc supports certain html formatting tags that allow this to be fixed:
	- <ul>, <li>, </li>, </ul>  allow creation of lists and list items
	- <pre>, </pre> (i.e. preformatted) retain the structure and enclose
		the structure in a gray bounding box
	- <p> (i.e. new paragraph) causes the following text to be started on
		a new line.
	- <b>,</b> (i.e. bold)

The list tags (<ul>, <li>) should be used to format bullet lists and the paragraph
tag (<p>) should be used whenever a sentence should be started as a new line. We
reformat the above comment as follows:

/**
  * This is the warp drive implementation module.
  * <p>It serves three purposes:<ul>
  * <li>The first purpose.</li>
  * <li>The second purpose.</li>
  * <li>The third purpose.</li></ul>
  **/

Note several things here:
- No bullet characters are used.  The <li> will cause the appropriate character
  to be inserted.
- Each sentence and bullet item is terminated with a period (.).  This is good
  practice to avoid inconsistent punctuation in bullet lists, which sometimes
  contain multiple sentences within a list item.  If it is certain that none of
  the list items will contain multiple sentences, then it is okay to avoid the
  period at the end of list items.

The new documentation string will be rendered as:

This is the warp drive implementation module.
It serves three purposes:
 o The first purpose.
 o The second purpose.
 o The third purpose.

Use of documentation tags

Certain aspects of the code documentation are specially rendered as separate
sections of the documentation.  These include:
- @param -- Parameter definitions.
- @return -- Return definitions.
- @field -- Field definitions.
- @value -- Value definitions e.g. for enumerations.
- @see -- References to other files or links.

These tags should always be used to describe the signature of the each ECL
attribute.  For example:

/**
  * Compute a logarithm of any base.
  * @param val The input value.  This must be a positive
  *            real number.
  * @param base The base of the logarithm.  This must be a
  *             positive real number greater than one.
  * @return A real number representing log(base)(val).
  * @see http://math.ucsd.edu/calculating-logs-of-arbitrary-bases.pdf
  **/

/**
  * Primary record structure for my process.
  * @field recordId The id of this record.  This must be unique within
  *                 A dataset.
  * @field state The state of current primary residence.
  ...
  **/
  
Other things to consider

Do not put a title or the name of the attribute into the documentation string.
The ECLdoc rendering includes the name of the attribute as well as its type.
The title or function name appear to be redundant after rendering.

For example:

/**
  * GenLog
  *
  * Compute a logarithm of any base.
  ...
  **/

This might be rendered as:

 GenLog: Genlog Compute a logarithm of any base.

The first sentence of the documentation string should be immediately descriptive
of the attribute as it is used to create a summary of the attribute when the
details of that attribute are collapsed.

For example:

/**
  * Use this as an alternative to existing ECL log functions when needing
  * a base other than e or 10.
  * Calculates a logarithm of any base.
  ...
  **/

The summary string might read: "Use this as an alternative to existing ECL", which
does not provide much insight into the purpose or function.

It is better to state the major function in the first few words, using the present
tense.  For example: "Compute a logarithm of any base".





