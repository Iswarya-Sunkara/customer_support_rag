with open('src/static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Close viewWeek10 before Week 12
target_1 = """                            </table>
                        </div>
                    </div>
                </div>

            <!-- ============================================================== -->
            <!-- Week 12: Production & Capstone — Tier-1 Deflection Assistant     -->"""

replacement_1 = """                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ============================================================== -->
            <!-- Week 12: Production & Capstone — Tier-1 Deflection Assistant     -->"""

assert target_1 in content, "target_1 not found"
content = content.replace(target_1, replacement_1)

# 2. Remove the extra closing tag before </main>
target_2 = """                        </div>
                    </div>
                </div>
            </div>

            </div>
        </main>"""

replacement_2 = """                        </div>
                    </div>
                </div>
            </div>
        </main>"""

assert target_2 in content, "target_2 not found"
content = content.replace(target_2, replacement_2)

# 3. Bump version to v=35
content = content.replace("app.js?v=30", "app.js?v=35")
content = content.replace("styles.css?v=30", "styles.css?v=35")

with open('src/static/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully fixed viewWeek10 closing tag and unnested viewWeek12!")

