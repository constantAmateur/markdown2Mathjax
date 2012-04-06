import re

def reconstructMath(processedString,codeblocks,inline_delims=["$","$"],equation_delims=["$$","$$"],htmlSafe=False):
    """This is usually the output of sanitizeInput, after having passed the output string through markdown.  The delimiters given to this function should match those used to construct the string to begin with.

     This will output a string containing html suitable to use with mathjax.
     
     "<" and ">" "&" symbols in math can confuse the html interpreter because they mark the begining and end of definition blocks.  To avoid issues, if htmlSafe is set to True these symbols will be replaced by ascii codes in the math blocks. The downside to this is that if anyone is already doing this, there already niced text might be mangled (I think I've taken steps to make sure it won't but not extensively tested...)"""
    placeholders=[inline_delims[0]+"1"+inline_delims[1],inline_delims[0]+"2"+inline_delims[1]]
    #Make html substitutions.
    if htmlSafe:
        safeAmp=re.compile("&(?!(?:amp;|lt;|gt;))")
        for i in xrange(2):
            for j in xrange(len(codeblocks[i])):
	        codeblocks[i][j]=safeAmp.sub("&amp;",codeblock[i][j])
	        codeblocks[i][j]=codeblocks[i][j].replace("<","&lt;")
	        codeblocks[i][j]=codeblocks[i][j].replace(">","&gt;")
    #Sub the inline blocks back in to the sanitized string
    outString=processedString
    for i in xrange(len(codeblocks[0])):
        outString=outString.replace(placeholders[0],inline_delims[0]+codeblocks[0][i]+inline_delims[1],1)
    #Sub the equation blocks back in to the sanitized string
    for i in xrange(len(codeblocks[1])):
        outString=outString.replace(placeholders[1],equation_delims[0]+codeblocks[1][i]+equation_delims[1],1)
    return outString
