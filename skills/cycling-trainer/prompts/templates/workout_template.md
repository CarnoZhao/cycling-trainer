# Workout 输出模板

> 被 commands/workout_generation.md、workout_adjustment.md 引用

## 输出格式

```
🚴 **Workout 生成**

👤 Carno  ⚡ FTP {ftp}w
📅 今天: {today} ({today_weekday})
━━━━━━━━━━━━━━━━━━━━━━

📅 **{date}** — **{name}**

```
{{description}}
```

⏱️ {{duration}}min · ⚡ NP ~{{np}}w · 📊 TSS ~{{tss}}

━━━━━━━━━━━━━━━━━━━━━━

**总结**: 共生成 **{workout_count}** 个 workouts

💡 调整还是上传？
• 调整：告诉我修改内容（如「周四改成3组」、「周六缩短到80分钟」）
• 上传：回复「上传」直接上传到 intervals.icu
```

## 休息日格式

```
📅 **{date}** — **🛌 完全休息**

今天安排完全休息，让身体恢复。
```

## 调整后的输出格式

```
🚴 **Workout 调整**

👤 Carno  ⚡ FTP {ftp}w
━━━━━━━━━━━━━━━━━━━━━━

{{#each workouts}}
📅 **{{date}}** — **{{name}}**

```
{{description}}
```

{{/each}}

━━━━━━━━━━━━━━━━━━━━━━
💡 调整还是上传？
• 调整：告诉我修改内容
• 上传：回复「上传」直接上传到 intervals.icu
```
