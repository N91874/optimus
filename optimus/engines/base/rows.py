from abc import abstractmethod, ABC

# This implementation works for Spark, Dask, dask_cudf
from optimus.helpers.columns import parse_columns
from optimus.helpers.constants import Actions
from optimus.infer import is_str, Infer


class BaseRows(ABC):
    """Base class for all Rows implementations"""

    def __init__(self, root):
        self.root = root

    @staticmethod
    @abstractmethod
    def create_id(column="id"):
        pass

    @abstractmethod
    def append(self, odfs, cols_map):
        pass

    #
    def greater_than(self, input_col, value):

        df = self.root.data
        return self.root.new(df[self.root.greather_than(input_col, value)])

    def greater_than_equal(self, input_col, value):

        df = self.root.data
        return self.root.new(df[self.root.greater_than_equal(input_col, value)])

    def less_than(self, input_col, value):

        df = self.root.data
        return self.root.new(df[self.root.less_than(input_col, value)])

    def less_than_equal(self, input_col, value):

        df = self.root.data
        return self.root.new(df[self.root.less_than_equal(input_col, value)])

    def equal(self, input_col, value):
        df = self.root.data
        return self.root.new(df[self.root.mask.is_equal(input_col, value)])

    def not_equal(self, input_col, value):

        df = self.root.data
        return self.root.new(df[self.root.mask.not_equal(input_col, value)])

    def missing(self, input_col):
        """
        Return missing values
        :param input_col:
        :return:
        """
        df = self.root.data
        return self.root.new(df[self.root.mask.missing(input_col)])

    def mismatch(self, input_col, dtype):
        """
        Return mismatches values
        :param input_col:
        :param dtype:
        :return:
        """
        df = self.root.data
        return self.root.new(df[self.root.mask.miasmatch(input_col, dtype)])

    def match(self, col_name, dtype):
        """
        Return Match values
        :param col_name:
        :param dtype:
        :return:
        """
        df = self.root.data
        return self.root.new(df[self.root.mask.match(col_name, dtype)])

    def apply(self, func, args=None, output_cols=None):
        """
        This will aimed to handle vectorized and not vectorized operations
        :param output_cols:
        :param func:
        :return:
        """
        df = self.root.data
        kw_columns = {}

        for output_col in output_cols:
            result = func(df, *args)
            kw_columns = {output_col: result}

        return df.assign(**kw_columns)

    def find(self, condition, output_col):
        """

        :param condition: a condition like (df.A > 0) & (df.B <= 10)
        :return:
        """
        df = self.root.data
        if is_str(condition):
            condition = eval(condition)

        df[output_col] = condition
        return self.root.new(df)

    def select(self, condition):
        """

        :param condition: a condition like (df.A > 0) & (df.B <= 10)
        :return:
        """

        df = self.root.data
        if is_str(condition):
            condition = eval(condition)
        df = df[condition]
        odf = self.root.new(df)
        meta = odf.meta.action(Actions.SORT_ROW.value, odf.cols.names())
        return self.root.new(odf.data, meta=meta)

    def count(self, compute=True) -> int:
        """
        Count dataframe rows
        """
        df = self.root.data
        # TODO: Be sure that we need the compute param
        if compute is True:
            result = df.count()
        else:
            result = df.count()
        return result

    def to_list(self, input_cols):
        """

        :param input_cols:
        :return:
        """
        odf = self.root
        input_cols = parse_columns(odf, input_cols)
        df = odf.cols.select(input_cols).to_pandas().values.tolist()

        return df

    @staticmethod
    @abstractmethod
    def sort(input_cols):
        pass

    def drop(self, where=None):
        """
        Drop a row depending on a dataframe expression
        :param where: Expression used to drop the row, For Ex: (df.A > 3) & (df.A <= 1000)
        :return: Spark DataFrame
        :return:
        """
        df = self.root.data
        if is_str(where):
            where = eval(where)

        df = df[~where]
        odf = self.root.new(df)
        meta = odf.meta.action(Actions.DROP_ROW.value, odf.cols.names())
        return self.root.new(odf.data, meta=meta)

    @staticmethod
    @abstractmethod
    def between(columns, lower_bound=None, upper_bound=None, invert=False, equal=False,
                bounds=None):
        pass

    @staticmethod
    @abstractmethod
    def drop_by_dtypes(input_cols, data_type=None):
        pass

    def drop_na(self, subset=None, how="any", *args, **kwargs):
        """
        Removes rows with null values. You can choose to drop the row if 'all' values are nulls or if
        'any' of the values is null.
        :param subset:
        :param how:
        :return:
        """
        df = self.root
        subset = parse_columns(df.data, subset)
        df.meta.set(df.meta.preserve(df, Actions.DROP_ROW.value, df.cols.names()).get())
        return self.root.new(df.dropna(how=how, subset=subset))

    @staticmethod
    @abstractmethod
    def drop_duplicates(input_cols=None):
        """
        Drop duplicates values in a dataframe
        :param input_cols: List of columns to make the comparison, this only  will consider this subset of columns,
        :return: Return a new DataFrame with duplicate rows removed
        :param input_cols:
        :return:
        """
        pass

    @staticmethod
    @abstractmethod
    def limit(count):
        """
        Limit the number of rows
        :param count:
        :return:
        """

        pass

    @staticmethod
    @abstractmethod
    def is_in(input_cols, values, output_cols=None):
        pass

    @staticmethod
    @abstractmethod
    def unnest(input_cols):
        pass

    def approx_count(self):
        """
        Aprox count
        :return:
        """
        return self.root.rows.count()
