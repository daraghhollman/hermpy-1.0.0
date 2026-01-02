import datetime as dt
import typing
from collections.abc import Sequence

DateLike: typing.TypeAlias = dt.date | dt.datetime
DateSequence = Sequence[DateLike]
