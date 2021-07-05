from typing import Dict, Optional
from abc import ABC, abstractclassmethod, abstractmethod

import discord

class BaseTask(ABC):
    """実行可能なすべての Task の抽象基底クラス。
    Task は特定の discord.py メソッドをラップしたもので、 `Task.execute()` コルーチンを呼び出して実際に実行できます。
    このクラスを用意したのは、設定ファイルの内容を Discord サーバーに反映する方法をできるだけ柔軟にするためです。

    Raises:
        NotImplementedError: 抽象基底クラスのため、直接メソッドを呼び出せません。
    """    
    @abstractmethod
    def execute(self):
        raise NotImplementedError()

class PartialDiscordModel(ABC):
    """部分的なDiscordモデルを示します。
    これは、設定ファイルを discord.py のデータクラスを使って整形したものです。
    """    
    pass

class BaseConverter(ABC):
    """あらゆるコンバーターが満たす必要がある抽象基底クラスです。
    `convert()` クラスメソッドで Discord モデルやデータクラスを組み込み型に変換し、 `parse()` クラスメソッドで Discord モデルに近い状態に整形します。
    """    
    @abstractclassmethod
    def convert(cls, target):
        """discord.py が提供する Discord モデルを組み込み型に変換します。

        Args:
            target (Any): 組み込み型に変換する Discord モデルやデータクラス。

        Raises:
            NotImplementedError: 抽象メソッドのため、呼び出すことができません。
        """        
        raise NotImplementedError()

    @abstractclassmethod
    def parse(cls, target):
        """`convert` メソッドによって取得されたオブジェクトを、 discord.py　の データクラスや PartialDiscordModel に変換します。

        Args:
            target (Any): `convert` メソッドで変換されたあとのオブジェクト。

        Raises:
            NotImplementedError: 抽象メソッドのため、呼び出すことができません。

        Returns:
            Any: [description]
        """        
        raise NotImplementedError()
        
class AbstractPermissionConverter(BaseConverter):
    """`discord.Permissions` についての変換を行うすべてのコンバーターが満たしている必要がある抽象クラスです。
    このクラスを実装することで、 `discord.Permissions` の変換時の挙動をカスタムできます。
    また、クラス変数を上書きすることで、 `discord.Permissions` を変換したあとの辞書のキーや値を変更することができます。
    """    
    allow = ''
    normal = ''

    add_reaction = ''
    administrator = ''
    attach_files = ''
    ban_members = ''
    change_nickname = ''
    connect = ''
    create_instant_invite = ''
    deafen_members = ''
    embed_links = ''
    external_emojis = ''
    kick_members = ''
    manage_channels = ''
    manage_emojis = ''
    manage_guild = ''
    manage_messages = ''
    manage_nicknames = ''
    manage_permissions = ''
    manage_roles = ''
    manage_webhooks = ''
    mention_everyone = ''
    move_members = ''
    mute_members = ''
    priority_speaker = ''
    read_message_history = ''

class AbstractRoleConverter(BaseConverter):
    """`discord.Role` についての変換を行うすべてのコンバーターが満たしている必要がある抽象クラスです。
    このクラスを実装することで、 `discord.Role` の変換時の挙動をカスタムできます。
    また、クラス変数を上書きすることで、 `discord.Role` を変換したあとの辞書のキーや値を変更することができます。
    """    
    key_id = ''
    key_name = ''
    key_colour = ''
    key_hoist = ''
    key_mentionable = ''
    key_position = ''
    key_permissions = ''

    permission_converter = AbstractPermissionConverter
    color_converter = BaseConverter

class AbstractGuildChannelConverter(BaseConverter):
    """`discord.Guild` についての変換を行うすべてのコンバーターが満たしている必要がある抽象クラスです。
    このクラスを実装することで、 `discord.Guild` の変換時の挙動をカスタムできます。
    また、クラス変数を上書きすることで、 `discord.Guild` を変換したあとの辞書のキーや値を変更することができます。
    """    
    key_id = ''
    key_name = ''
    key_position = ''
    key_overwrites = ''
    key_type = ''

    channel_type = ''
    
class AbstractTextChannelConverter(AbstractGuildChannelConverter):
    key_topic = ''
    key_nsfw = ''
    key_news = ''

class AbstractVoiceChannelConverter(AbstractGuildChannelConverter):
    key_bitrate = ''
    key_user_limit = ''
    key_rtc_region = ''

class AbstractStoreChannelConverter(AbstractGuildChannelConverter):
    key_nsfw = ''

class AbstractStageChannelConverter(AbstractVoiceChannelConverter):
    key_topic = ''

class AbstractCategoryChannelConverter(AbstractGuildChannelConverter):
    key_nsfw = ''
    key_channels = ''

class AbstractVoiceRegionConverter(BaseConverter):
    amsterdam = ''
    brazil = ''
    dubai = ''
    eu_central = ''
    eu_west = ''
    europe = ''
    frankfurt = ''
    hongkong = ''
    india = ''
    japan = ''
    london = ''
    russia = ''
    singapore = ''
    south_korea = ''
    southafrica = ''
    sydney = ''
    us_central = ''
    us_east = ''
    us_south = ''
    us_west = ''
    vip_amsterdam = ''
    vip_us_east = ''
    vip_us_west = ''

class AbstractGuildConverter(BaseConverter):
    key_id = ''
    key_name = ''
    key_channels = ''
    key_roles = ''

class AbstractChannelConverterGetter():
    @abstractclassmethod
    def get_converter(cls, channel: discord.abc.GuildChannel) -> Optional[AbstractGuildChannelConverter]:
        """discord.abc.GuildChannel インスタンスを受け取り、対応する辞書変換コンバーターを返します。

        Args:
            channel (discord.abc.GuildChannel): [description]

        Raises:
            NotImplementedError: [description]

        Returns:
            Optional[AbstractGuildChannelConverter]: 適切なコンバーターが見つかればその `AbstractGuildChannelConverter` を返します。見つからなければ `None` が返ります。
        """        
        raise NotImplementedError()

    @abstractclassmethod
    def get_parser(cls, channel_dict: Dict) -> Optional[AbstractGuildChannelConverter]:
        """変換後のチャンネル辞書を受け取り、対応する部分モデル変換パーサーを返します。
        デフォルトの実装では、チャンネル辞書の type キーからパーサーを検索するようになっています。

        Args:
            channel_dict (Dict): [description]

        Returns:
            Optional[AbstractGuildChannelConverter]: 適切なパーサーが見つかればその `AbstractGuildChannelConverter` を返します。見つからなければ `None` を返ります。
        """        