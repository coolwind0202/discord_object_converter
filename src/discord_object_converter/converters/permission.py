from typing import Dict

import discord

from .abstract import AbstractPermissionConverter

class PermissionConverter(AbstractPermissionConverter):
    allow = 'OK'
    normal = 'NG'

    add_reactions = 'リアクションの追加'
    administrator = '管理者'
    attach_files = 'ファイルを添付'
    ban_members = 'メンバーをBAN'
    change_nickname = 'ニックネームの変更'
    connect = '接続'
    create_instant_invite = '招待の作成'
    deafen_members = 'メンバーのスピーカーをミュート'
    embed_links = '埋め込みリンク'
    external_emojis = '外部の絵文字を使用する'
    kick_members = 'メンバーをキック'
    manage_channels = 'チャンネルの管理'
    manage_emojis = '絵文字の管理'
    manage_guild = 'サーバーの管理'
    manage_messages = 'メッセージの管理'
    manage_nicknames = 'ニックネームの管理'
    manage_permissions = '権限の管理'
    manage_roles = 'ロールの管理'
    manage_webhooks = 'ウェブフックの管理'
    mention_everyone = '@everyone、 @here、 全てのロールにメンション'
    move_members = 'メンバーを移動'
    mute_members = 'メンバーをミュート'
    priority_speaker = '優先スピーカー'
    read_message_history = 'メッセージ履歴を読む'
    read_messages = 'メッセージを読む'
    request_to_speak = 'スピーカー参加をリクエスト'
    send_messages = 'メッセージを送信'
    send_tts_messages = 'テキスト読み上げメッセージを送信する'
    speak = '発言'
    stream = '動画'
    view_guild_insights = 'サーバーインサイトを見る'
    use_slash_commands = 'スラッシュコマンドを使用'
    view_audit_log = '監査ログを表示'
    view_channel = 'チャンネルを見る'

    @classmethod
    def convert(cls, target: discord.Permissions) -> Dict[str, str]:
        result = {}
        for perm in target:
            perm_name, perm_value = perm

            perm_japanese_name = getattr(cls, perm_name, perm_name)
            if not perm_japanese_name:
                perm_japanese_name = perm_name  #  権限の日本語名が設定されていない ( 空文字 ) 場合は元の権限名を使う

            result[perm_japanese_name] = cls.allow if perm_value else cls.normal
        return result

    @classmethod
    def parse(cls, target: Dict) -> discord.Permissions:
        permission = discord.Permissions()
        for perm in permission:
            perm_name, _ = perm

            perm_japanese_name = getattr(cls, perm_name, perm_name)
            setattr(permission, perm_name, target[perm_japanese_name] == cls.allow)
        return permission