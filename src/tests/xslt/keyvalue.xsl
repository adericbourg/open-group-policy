<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
				<xsl:output method="text" encoding="UTF-8" />

				<xsl:template match="/">
								<xsl:for-each select="conf/key">
												<xsl:choose>
																<xsl:when test="@type = 'string'">
																				<xsl:value-of select="@name"/>=<xsl:text>&quot;</xsl:text><xsl:value-of select="."/><xsl:text>&quot;&#xa;</xsl:text>
																</xsl:when>
																<xsl:otherwise>
																				<xsl:value-of select="@name"/>=<xsl:value-of select="."/><xsl:text>&#xa;</xsl:text>
																</xsl:otherwise>
												</xsl:choose>
								</xsl:for-each>
				</xsl:template>
</xsl:stylesheet>
