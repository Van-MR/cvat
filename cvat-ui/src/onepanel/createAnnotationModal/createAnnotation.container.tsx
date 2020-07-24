// Copyright (C) 2020 Intel Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import { connect } from 'react-redux';

// import ModelRunnerModalComponent from 'components/model-runner-modal/model-runner-modal';
import ModelNewAnnotationModalComponent from './createAnnotaion.component';
import {
    CombinedState,
} from 'reducers/interfaces';
import {
    createAnnotationAction,
    getBaseModelsAsync,
} from './createAnnotation.action';


interface StateToProps {
    taskInstance: any;
    visible: boolean;
    baseModelList: string[];
}

interface DispatchToProps {
    closeDialog(): void;
    getBaseModelList(taskInstance: any, modelType: string): void;
}

function mapStateToProps(state: CombinedState): StateToProps {
    const { models } = state;

    return {
        taskInstance: models.activeNewAnnotationTask,
        visible: models.visibleNewAnnotationWindows,
        baseModelList: models.baseModelList,
    };
}

function mapDispatchToProps(dispatch: any): DispatchToProps {
    return ({
        closeDialog(): void {
            dispatch(createAnnotationAction.closeNewAnnotationDialog());
        },
        getBaseModelList(taskInstance, modelType): void {
            dispatch(getBaseModelsAsync(taskInstance, modelType));
        }
    });
}


function ModelNewAnnotationModalContainer(props: StateToProps & DispatchToProps): JSX.Element {
    return (
        <ModelNewAnnotationModalComponent {...props} />
    );
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ModelNewAnnotationModalContainer);
