// music-tools — MCP server for the Rainbow Tots channel.
//
// Tools:
//   create_song  – sends a song request to a music-generation service you configure
//                  (MUSIC_API_URL + MUSIC_API_KEY). Without them it explains what is missing.
//   clean_vocal  – cleans, time-aligns and tunes a real vocal take to one of our songs
//                  (runs kids/../voice_real/make_vocal.py locally; works offline).
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const run = promisify(execFile);
const HERE = path.dirname(fileURLToPath(import.meta.url));
const KIDS = path.resolve(HERE, "../kids");

const server = new Server(
  { name: "music-tools", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

const TOOLS = [
  {
    name: "create_song",
    description: "Создаёт детскую песню через подключённый сервис генерации музыки (нужны MUSIC_API_URL и MUSIC_API_KEY).",
    inputSchema: {
      type: "object",
      properties: {
        prompt: { type: "string", description: "Стиль и настроение, например: cheerful kids song, ukulele, 120 bpm" },
        lyrics: { type: "string", description: "Текст песни (необязательно)" }
      },
      required: ["prompt"]
    }
  },
  {
    name: "clean_vocal",
    description: "Чистит запись голоса, выравнивает её по ритму и подстраивает ноты под песню канала.",
    inputSchema: {
      type: "object",
      properties: {
        take: { type: "string", description: "Путь к записи голоса (wav/mp3/m4a)" },
        song: { type: "string", description: "Папка песни, например build_intro или build_tiko" },
        segments: { type: "string", description: "Где в записи каждая нота: '0.68-1.82,1.84-2.58,2.62-3.85'" },
        out: { type: "string", description: "Куда сохранить чистый вокал (wav)" }
      },
      required: ["take", "song", "segments", "out"]
    }
  }
];

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

const text = (t, isError = false) => ({ content: [{ type: "text", text: t }], isError });

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args = {} } = request.params;

  if (name === "create_song") {
    const url = process.env.MUSIC_API_URL, key = process.env.MUSIC_API_KEY;
    if (!url || !key) {
      return text("Сервис генерации музыки не подключён: задайте MUSIC_API_URL и MUSIC_API_KEY в настройках MCP-сервера. " +
        "Формат запроса зависит от сервиса — проверьте его документацию.", true);
    }
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${key}` },
        body: JSON.stringify({ prompt: args.prompt, lyrics: args.lyrics ?? "" })
      });
      const body = await res.text();
      if (!res.ok) return text(`Сервис ответил ошибкой ${res.status}: ${body.slice(0, 500)}`, true);
      return text(`Песня отправлена на генерацию. Ответ сервиса: ${body.slice(0, 2000)}`);
    } catch (e) {
      return text(`Не удалось связаться с сервисом: ${e.message}`, true);
    }
  }

  if (name === "clean_vocal") {
    const take = path.resolve(KIDS, args.take);
    const songJson = path.resolve(KIDS, args.song, "song.json");
    const out = path.resolve(KIDS, args.out);
    if (!existsSync(take)) return text(`Файл записи не найден: ${take}`, true);
    if (!existsSync(songJson)) return text(`Песня не найдена: ${songJson}`, true);
    let wav = take;
    if (!take.toLowerCase().endsWith(".wav")) {           // m4a/mp3 -> wav
      wav = take.replace(/\.[^.]+$/, "") + "_mcp.wav";
      await run("ffmpeg", ["-y", "-loglevel", "error", "-i", take, "-ac", "1", "-ar", "48000", wav]);
    }
    try {
      const { stdout } = await run("python3", [path.join(KIDS, "voice_real/make_vocal.py"), wav, songJson, out, args.segments], { cwd: KIDS });
      return text(stdout.trim());
    } catch (e) {
      return text(`Ошибка обработки: ${(e.stderr || e.message).toString().slice(-800)}`, true);
    }
  }

  return text(`Неизвестный инструмент: ${name}`, true);
});

await server.connect(new StdioServerTransport());
